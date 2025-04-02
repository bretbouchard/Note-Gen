import pytest
from httpx import AsyncClient
import asyncio

@pytest.mark.asyncio
async def test_request_validation(test_client: AsyncClient):
    """Test validation middleware with invalid request."""
    response = await test_client.post("/api/v1/patterns/", json={})
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_rate_limiting(test_client: AsyncClient):
    """Test rate limiting middleware."""
    # Make multiple requests to trigger rate limit
    for _ in range(60):  # Increased to hit the rate limit
        await test_client.get("/api/v1/patterns/")
        await asyncio.sleep(0.01)  # Small delay to prevent overwhelming

    response = await test_client.get("/api/v1/patterns/")
    assert response.status_code == 429
    assert "error" in response.json()
