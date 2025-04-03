"""Simple tests for the validation router."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from note_gen.routers.validation import router


@pytest.fixture
def app():
    """Create a test app with the validation router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


def test_validate_note_pattern_endpoint_exists(client):
    """Test that the validate note pattern endpoint exists."""
    response = client.post(
        "/note-pattern",
        json={
            "name": "Test Pattern",
            "complexity": 3.0,
            "tags": ["test"],
            "data": {
                "notes": [{"pitch": "C", "octave": 4, "duration": 1.0, "velocity": 100}],
                "scale_type": "MAJOR",
                "direction": "up"
            }
        }
    )
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_validate_rhythm_pattern_endpoint_exists(client):
    """Test that the validate rhythm pattern endpoint exists."""
    response = client.post(
        "/rhythm-pattern",
        json={
            "name": "Test Rhythm",
            "time_signature": [4, 4],
            "notes": [{"position": 0, "duration": 1.0, "velocity": 100}]
        }
    )
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_validate_chord_progression_endpoint_exists(client):
    """Test that the validate chord progression endpoint exists."""
    response = client.post(
        "/chord-progression",
        json={
            "name": "Test Progression",
            "key": "C",
            "scale_type": "MAJOR",
            "chords": []
        }
    )
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_validate_config_endpoint_exists(client):
    """Test that the validate config endpoint exists."""
    response = client.post(
        "/config",
        json={
            "config": {"key": "value"},
            "config_type": "test_config"
        }
    )
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404
