"""Tests for the validation router."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from note_gen.routers.validation import router
from note_gen.controllers.validation_controller import ValidationController
from note_gen.core.enums import ValidationLevel
from note_gen.validation.base_validation import ValidationResult, ValidationViolation


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


@pytest.fixture
def mock_controller():
    """Create a mock validation controller."""
    controller = AsyncMock(spec=ValidationController)
    return controller


def test_validate_note_pattern(client, mock_controller):
    """Test the validate note pattern endpoint."""
    # Setup mock
    mock_controller.validate_note_pattern.return_value = ValidationResult(
        is_valid=True,
        violations=[]
    )
    
    # Patch the dependency
    with patch("note_gen.routers.validation.get_validation_controller", return_value=mock_controller):
        # Call endpoint
        response = client.post(
            "/note-pattern",
            json={
                "name": "Test Pattern",
                "complexity": 3.0,
                "tags": ["test"],
                "data": {
                    "notes": [{"pitch": 60, "duration": 1.0, "velocity": 100}],
                    "scale_type": "MAJOR",
                    "direction": "ASCENDING"
                }
            }
        )
        
        # Verify
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        assert len(response.json()["violations"]) == 0
        mock_controller.validate_note_pattern.assert_called_once()


def test_validate_note_pattern_invalid(client, mock_controller):
    """Test the validate note pattern endpoint with invalid data."""
    # Setup mock
    mock_controller.validate_note_pattern.return_value = ValidationResult(
        is_valid=False,
        violations=[
            ValidationViolation(
                message="Invalid note pattern",
                severity=ValidationLevel.ERROR
            )
        ]
    )
    
    # Patch the dependency
    with patch("note_gen.routers.validation.get_validation_controller", return_value=mock_controller):
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
        mock_controller.validate_note_pattern.assert_called_once()


def test_validate_rhythm_pattern(client, mock_controller):
    """Test the validate rhythm pattern endpoint."""
    # Setup mock
    mock_controller.validate_rhythm_pattern.return_value = ValidationResult(
        is_valid=True,
        violations=[]
    )
    
    # Patch the dependency
    with patch("note_gen.routers.validation.get_validation_controller", return_value=mock_controller):
        # Call endpoint
        response = client.post(
            "/rhythm-pattern",
            json={
                "name": "Test Rhythm",
                "time_signature": [4, 4],
                "notes": [{"position": 0, "duration": 1.0, "velocity": 100}]
            }
        )
        
        # Verify
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        assert len(response.json()["violations"]) == 0
        mock_controller.validate_rhythm_pattern.assert_called_once()


def test_validate_chord_progression(client, mock_controller):
    """Test the validate chord progression endpoint."""
    # Setup mock
    mock_controller.validate_chord_progression.return_value = ValidationResult(
        is_valid=True,
        violations=[]
    )
    
    # Patch the dependency
    with patch("note_gen.routers.validation.get_validation_controller", return_value=mock_controller):
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
        
        # Verify
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        assert len(response.json()["violations"]) == 0
        mock_controller.validate_chord_progression.assert_called_once()


def test_validate_config(client, mock_controller):
    """Test the validate config endpoint."""
    # Setup mock
    mock_controller.validate_config.return_value = True
    
    # Patch the dependency
    with patch("note_gen.routers.validation.get_validation_controller", return_value=mock_controller):
        # Call endpoint
        response = client.post(
            "/config",
            json={
                "config": {"key": "value"},
                "config_type": "test_config"
            }
        )
        
        # Verify
        assert response.status_code == 200
        assert response.json()["is_valid"] is True
        mock_controller.validate_config.assert_called_once()
