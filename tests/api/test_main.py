import pytest
from fastapi.testclient import TestClient

def test_get_patterns(client):
    response = client.get("/api/v1/patterns")
    assert response.status_code == 200
    data = response.json()
    assert "rhythm_patterns" in data
    assert "note_patterns" in data
