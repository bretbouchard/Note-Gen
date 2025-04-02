import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_patterns(test_client: AsyncClient):
    """Test getting patterns endpoint."""
    response = await test_client.get("/api/v1/patterns/", follow_redirects=True)
    assert response.status_code == 200
