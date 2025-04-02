"""Test pattern fetching endpoints."""
import pytest
from httpx import AsyncClient
from bson import ObjectId

pytestmark = pytest.mark.asyncio

class TestPatternFetching:
    async def test_fetch_pattern_by_id(self, test_client: AsyncClient):
        # First create a pattern
        pattern_data = {
            "name": "Test Pattern",
            "pattern_type": "note",  # Add required field
            "pattern": [{"note": "C4", "duration": 1.0}]
        }
        create_response = await test_client.post("/api/v1/patterns/", json=pattern_data)
        assert create_response.status_code == 201
        pattern_id = create_response.json()["id"]

        # Then fetch it
        response = await test_client.get(f"/api/v1/patterns/{pattern_id}")
        assert response.status_code == 200
        assert "data" in response.json()
        assert response.json()["data"]["name"] == "Test Pattern"

    async def test_fetch_nonexistent_pattern(self, test_client: AsyncClient):
        nonexistent_id = str(ObjectId())
        response = await test_client.get(f"/api/v1/patterns/{nonexistent_id}")
        assert response.status_code == 404
        assert "Pattern not found" in response.json()["detail"]

    async def test_database_error(self, test_client: AsyncClient, monkeypatch):
        def mock_db_error(*args, **kwargs):
            raise Exception("Database error")

        # Mock the ObjectId constructor to raise an exception
        monkeypatch.setattr(
            "bson.ObjectId",
            mock_db_error
        )

        response = await test_client.get(f"/api/v1/patterns/{str(ObjectId())}")
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]


