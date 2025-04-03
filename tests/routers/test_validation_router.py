"""Tests for the validation router."""
import pytest
from unittest.mock import patch
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





def test_validate_note_pattern(client):
    """Test the validate note pattern endpoint."""
    # Patch the endpoint function directly
    with patch("note_gen.routers.validation.validate_note_pattern", return_value={"is_valid": True, "violations": []}):
        # Call endpoint
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

        # Verify response
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        assert len(response.json()["violations"]) == 0


def test_validate_note_pattern_invalid(client):
    """Test the validate note pattern endpoint with invalid data."""
    # Patch the endpoint function directly
    with patch("note_gen.routers.validation.validate_note_pattern", return_value={
        "is_valid": False,
        "violations": [{"message": "Invalid note pattern", "code": "VALIDATION_ERROR", "path": ""}]
    }):
        # Call endpoint
        response = client.post(
            "/note-pattern",
            json={
                "name": "Invalid Pattern"
            }
        )

        # Verify
        assert response.status_code == 200
        assert response.json()["is_valid"] is False
        assert len(response.json()["violations"]) == 1
        assert response.json()["violations"][0]["message"] == "Invalid note pattern"


def test_validate_rhythm_pattern(client):
    """Test the validate rhythm pattern endpoint."""
    # Patch the endpoint function directly
    with patch("note_gen.routers.validation.validate_rhythm_pattern", return_value={"is_valid": True, "violations": []}):
        # Call endpoint
        response = client.post(
            "/rhythm-pattern",
            json={
                "name": "Test Rhythm",
                "time_signature": [4, 4],
                "notes": [{"position": 0, "duration": 1.0, "velocity": 100}]
            }
        )

        # Verify response
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        assert len(response.json()["violations"]) == 0


def test_validate_chord_progression(client):
    """Test the validate chord progression endpoint."""
    # Patch the endpoint function directly
    with patch("note_gen.routers.validation.validate_chord_progression", return_value={"is_valid": True, "violations": []}):
        # Call endpoint
        response = client.post(
            "/chord-progression",
            json={
                "name": "Test Progression",
                "key": "C",
                "scale_type": "MAJOR",
                "chords": []
            }
        )

        # Verify response
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        assert len(response.json()["violations"]) == 0


def test_validate_config(client):
    """Test the validate config endpoint."""
    # Patch the endpoint function directly
    with patch("note_gen.routers.validation.validate_config", return_value={"is_valid": True}):
        # Call endpoint
        response = client.post(
            "/config",
            json={
                "config": {"key": "value"},
                "config_type": "test_config"
            }
        )

        # Verify response
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
