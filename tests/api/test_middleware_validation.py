import pytest
from src.note_gen.api.errors import ErrorCodes
from httpx import AsyncClient

class TestRequestValidation:
    @pytest.mark.asyncio
    async def test_missing_content_type(self, test_client: AsyncClient):
        """Test request without content-type header."""
        response = await test_client.post(
            "/api/v1/patterns/",
            content=b'{"name": "Test"}'
        )
        assert response.status_code == 422  # Updated expected status code
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_valid_request(self, test_client: AsyncClient):
        """Test valid request passes middleware."""
        response = await test_client.post(
            "/api/v1/patterns/",
            json={"name": "Test Pattern", "pattern": [{"pitch": 60, "duration": 1.0}]},
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 201  # The pattern_api.py endpoint returns 201 for successful creation
