import pytest
from httpx import AsyncClient
import logging

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_get_patterns(test_client: AsyncClient):
    """Test patterns endpoint."""
    response = await test_client.get("/api/v1/patterns/note-patterns")
    assert response.status_code == 200
    data = response.json()
    assert "patterns" in data

@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient):
    """Test health check endpoint."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
