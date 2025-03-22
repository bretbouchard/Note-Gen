import pytest
from src.note_gen.core.constants import RATE_LIMIT

class TestMiddlewareIntegration:
    @pytest.fixture
    def endpoint(self):
        return "/test"

    @pytest.fixture(autouse=True)
    def reset_rate_limit(self):
        from src.note_gen.api.middleware.rate_limit import rate_limit_store
        rate_limit_store.clear()
        yield

    def test_validation_with_rate_limit(self, test_client, endpoint):
        headers = {"content-type": "application/json"}
        responses = []
        
        # Make multiple requests
        for _ in range(RATE_LIMIT + 1):
            response = test_client.get(endpoint, headers=headers)
            responses.append(response)
            
        # At least one response should be rate limited
        assert any(r.status_code == 429 for r in responses)

    def test_error_handling_precedence(self, test_client, endpoint):
        # Invalid JSON should trigger validation error before rate limit
        response = test_client.post(
            endpoint,
            content=b'invalid json',
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDATION_ERROR"
