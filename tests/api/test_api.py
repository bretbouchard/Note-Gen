import pytest
import httpx
from httpx import AsyncClient
from src.note_gen.main import app
import logging

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_get_patterns(test_client: AsyncClient):
    """Test patterns endpoint."""
    response = await test_client.get("/api/v1/patterns/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient):
    """Test health check endpoint."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
