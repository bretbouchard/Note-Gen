import pytest
from httpx import AsyncClient
import asyncio
from unittest.mock import patch
from src.note_gen.app import limiter  # Import the limiter instance directly from app

class TestRateLimiting:
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, test_client: AsyncClient):
        """Test that rate limiting works correctly."""
        endpoint = "/api/v1/patterns/"
        
        # Clear any existing rate limit data
        limiter.reset()
        
        # Make requests up to the limit
        for _ in range(61):  # One more than the limit
            await test_client.get(endpoint)
            await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
        
        # This request should be rate limited
        response = await test_client.get(endpoint)
        assert response.status_code == 429
        assert "error" in response.json()

    @pytest.mark.asyncio
    async def test_rate_limit_reset(self, test_client: AsyncClient):
        """Test that rate limit resets after the specified time."""
        endpoint = "/api/v1/patterns/"
        
        # Clear any existing rate limit data
        limiter.reset()
        
        # Make initial requests
        for _ in range(3):
            response = await test_client.get(endpoint)
            assert response.status_code == 200

        # Reset the limiter
        limiter.reset()
        
        # Should be able to make requests again
        response = await test_client.get(endpoint)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_with_mocked_time(self, test_client: AsyncClient):
        """Test rate limit with mocked time."""
        endpoint = "/api/v1/patterns/"
        
        # Clear any existing rate limit data
        limiter.reset()

        # Make requests up to the limit
        for _ in range(60):  # Hit the full limit
            response = await test_client.get(endpoint)
            assert response.status_code == 200

        # This request should be rate limited
        response = await test_client.get(endpoint)
        assert response.status_code == 429  # Should be rate limited

        with patch('time.time') as mock_time:
            # Set initial time
            current_time = 1000.0  # arbitrary start time
            mock_time.return_value = current_time
            
            # Verify we're still rate limited
            response = await test_client.get(endpoint)
            assert response.status_code == 429

            # Move time forward past the window (60 seconds)
            mock_time.return_value = current_time + 61
            
            # Reset the limiter to simulate time passing
            limiter.reset()
            
            # Should be able to make requests again
            response = await test_client.get(endpoint)
            assert response.status_code == 200
