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

@pytest.mark.asyncio
async def test_validation_error_handling(test_client: AsyncClient):
    """Test validation error handling."""
    # Send invalid data (missing required fields)
    invalid_data = {
        "incomplete": "data"
    }
    response = await test_client.post("/api/v1/patterns/", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_database_error_handling(test_client: AsyncClient):
    """Test database error handling."""
    # Try to fetch a non-existent pattern
    response = await test_client.get("/api/v1/patterns/invalid_id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()
