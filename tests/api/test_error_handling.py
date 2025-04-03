"""Test error handling in the API."""
import pytest
from fastapi import status
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_exception_handling(test_client: AsyncClient):
    """Test general API exception handling."""
    # Try to access an invalid endpoint
    response = await test_client.get("/api/v1/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND
