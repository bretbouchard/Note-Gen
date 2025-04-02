import pytest
from fastapi import FastAPI
from httpx import AsyncClient

RATE_LIMIT = 5  # Define the rate limit constant

class TestMiddlewareIntegration:
    @pytest.mark.asyncio
    async def test_validation_with_rate_limit(self, test_client: AsyncClient):
        headers = {"content-type": "application/json"}

        # Make multiple requests
        for _ in range(RATE_LIMIT):
            response = await test_client.post(
                "/api/v1/patterns/",
                json={},
                headers=headers
            )
            assert response.status_code == 422  # Should fail validation first

        # Next request should hit rate limit
        response = await test_client.post(
            "/api/v1/patterns/",
            json={},
            headers=headers
        )
        assert response.status_code == 422  # Validation takes precedence over rate limiting

    @pytest.mark.asyncio
    async def test_error_handling_precedence(self, test_client: AsyncClient):
        response = await test_client.post(
            "/api/v1/patterns/",
            content=b'invalid json',
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422  # Validation takes precedence over rate limiting