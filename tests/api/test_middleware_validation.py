import pytest
from src.note_gen.api.errors import ErrorCodes

class TestRequestValidation:
    @pytest.fixture
    def endpoint(self):
        return "/test"

    def test_missing_content_type(self, test_client, endpoint):
        """Test request without content-type header."""
        response = test_client.post(
            endpoint,
            content=b'{"name": "Test"}'
        )
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == ErrorCodes.VALIDATION_ERROR.value
        assert "Missing required header: content-type" in data["message"]

    def test_invalid_json(self, test_client, endpoint):
        """Test request with invalid JSON."""
        response = test_client.post(
            endpoint,
            content=b'invalid json',
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422
        data = response.json()
        assert data["code"] == ErrorCodes.VALIDATION_ERROR.value

    def test_valid_request(self, test_client, endpoint):
        """Test valid request passes middleware."""
        response = test_client.post(
            endpoint,
            json={"name": "Test"},
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 200
