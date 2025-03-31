import pytest
from fastapi.testclient import TestClient
from src.note_gen.main import app
import time

client = TestClient(app)

def test_request_validation():
    """Test request validation middleware."""
    # Test missing required fields
    response = client.post(
        "/generate/progression",
        json={},
        headers={"content-type": "application/json"}
    )
    assert response.status_code == 422
    assert "validation error" in response.json()["detail"][0]["msg"].lower()
    
    # Test missing content-type header
    response = client.post("/generate/progression", json={})
    assert response.status_code == 400
    assert "Missing required header" in response.json()["message"]
    
    # Test valid request
    valid_data = {
        "name": "Test Progression",
        "key": "C",
        "scale_type": "MAJOR",
        "chords": []
    }
    response = client.post(
        "/generate/progression",
        json=valid_data,
        headers={"content-type": "application/json"}
    )
    assert response.status_code == 200

def test_rate_limiting():
    """Test rate limiting middleware."""
    # Make requests up to the limit
    for _ in range(100):  # RATE_LIMIT is 100
        response = client.get("/presets/progressions")
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get("/presets/progressions")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["message"]
    
    # Wait for rate limit window to reset
    time.sleep(60)
    response = client.get("/presets/progressions")
    assert response.status_code == 200
