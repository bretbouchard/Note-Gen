import time
import pytest
from src.note_gen.core.constants import RATE_LIMIT
from src.note_gen.api.errors import ErrorCodes
from src.note_gen.api.middleware.rate_limit import rate_limiter

class TestRateLimiting:
    @pytest.fixture
    def endpoint(self):
        return "/test"

    @pytest.fixture(autouse=True)
    def setup(self):
        rate_limiter.clear()
        yield

    def test_rate_limit_exceeded(self, test_client, endpoint):
        headers = {"content-type": "application/json"}
        
        # Make requests exactly up to the limit
        for _ in range(RATE_LIMIT):
            response = test_client.get(endpoint, headers=headers)
            assert response.status_code == 200, f"Failed on request with status {response.status_code}"
            
        # Next request should be rate limited
        response = test_client.get(endpoint, headers=headers)
        assert response.status_code == 429
        assert response.json()["code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value

    def test_rate_limit_reset(self, test_client, endpoint):
        headers = {"content-type": "application/json"}
        
        # Fill up to the limit
        for _ in range(RATE_LIMIT):
            response = test_client.get(endpoint, headers=headers)
            assert response.status_code == 200
            
        # Verify rate limit is hit
        response = test_client.get(endpoint, headers=headers)
        assert response.status_code == 429
        
        # Clear the rate limiter (simulating time passage)
        rate_limiter.clear()
        
        # Should work again
        response = test_client.get(endpoint, headers=headers)
        assert response.status_code == 200

    def test_concurrent_requests(self, test_client, endpoint):
        headers = {"content-type": "application/json"}
        
        # Make concurrent requests
        responses = []
        for _ in range(RATE_LIMIT + 5):
            response = test_client.get(endpoint, headers=headers)
            responses.append(response)
            
        # Verify some responses were rate limited
        success_count = sum(1 for r in responses if r.status_code == 200)
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        
        assert success_count <= RATE_LIMIT
        assert rate_limited_count > 0
