"""Tests for the utility router."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from note_gen.routers.utility import router
from note_gen.controllers.utility_controller import UtilityController


@pytest.fixture
def app():
    """Create a test app with the utility router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_controller():
    """Create a mock utility controller."""
    controller = AsyncMock(spec=UtilityController)
    return controller


def test_health_check(client, mock_controller):
    """Test the health check endpoint."""
    # Setup mock
    mock_controller.health_check.return_value = {"status": "ok"}
    
    # Patch the dependency
    with patch("note_gen.routers.utility.get_utility_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/health")
        
        # Verify
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_controller.health_check.assert_called_once()


def test_get_statistics(client, mock_controller):
    """Test the statistics endpoint."""
    # Setup mock
    mock_controller.get_statistics.return_value = {
        "statistics": {
            "chord_progressions": 10,
            "note_patterns": 20,
            "rhythm_patterns": 15,
            "sequences": 5,
            "users": 3
        },
        "details": {
            "note_patterns_by_scale": {"MAJOR": 10, "MINOR": 10},
            "chord_progressions_by_key": {"C": 5, "G": 5},
            "rhythm_patterns_by_time_signature": {"4/4": 10, "3/4": 5}
        }
    }
    
    # Patch the dependency
    with patch("note_gen.routers.utility.get_utility_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/stats")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["statistics"]["chord_progressions"] == 10
        assert data["statistics"]["note_patterns"] == 20
        assert data["statistics"]["rhythm_patterns"] == 15
        assert data["statistics"]["sequences"] == 5
        assert data["statistics"]["users"] == 3
        assert data["details"]["note_patterns_by_scale"]["MAJOR"] == 10
        assert data["details"]["chord_progressions_by_key"]["C"] == 5
        assert data["details"]["rhythm_patterns_by_time_signature"]["4/4"] == 10
        mock_controller.get_statistics.assert_called_once()


def test_list_all_patterns(client, mock_controller):
    """Test the patterns list endpoint."""
    # Setup mock
    mock_controller.list_all_patterns.return_value = {
        "note_patterns": [
            {"id": "1", "name": "Test Pattern 1", "type": "note_pattern"},
            {"id": "2", "name": "Test Pattern 2", "type": "note_pattern"}
        ],
        "rhythm_patterns": [
            {"id": "3", "name": "Test Rhythm 1", "type": "rhythm_pattern"},
            {"id": "4", "name": "Test Rhythm 2", "type": "rhythm_pattern"}
        ],
        "chord_progressions": [
            {"id": "5", "name": "Test Progression 1", "type": "chord_progression", "key": "C", "scale_type": "MAJOR"},
            {"id": "6", "name": "Test Progression 2", "type": "chord_progression", "key": "G", "scale_type": "MINOR"}
        ]
    }
    
    # Patch the dependency
    with patch("note_gen.routers.utility.get_utility_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/patterns-list")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data["note_patterns"]) == 2
        assert len(data["rhythm_patterns"]) == 2
        assert len(data["chord_progressions"]) == 2
        assert data["note_patterns"][0]["name"] == "Test Pattern 1"
        assert data["rhythm_patterns"][0]["name"] == "Test Rhythm 1"
        assert data["chord_progressions"][0]["name"] == "Test Progression 1"
        mock_controller.list_all_patterns.assert_called_once()


def test_get_api_info(client, mock_controller):
    """Test the API info endpoint."""
    # Setup mock
    mock_controller.get_api_info.return_value = {
        "app": "Note Generator API",
        "version": "1.0.0",
        "description": "API for musical pattern generation and manipulation",
        "documentation": "/docs",
        "endpoints": [
            "/api/v1/chord-progressions",
            "/api/v1/patterns",
            "/api/v1/sequences",
            "/api/v1/users",
            "/api/v1/validation",
            "/api/v1/import-export",
            "/health",
            "/stats",
            "/patterns-list"
        ]
    }
    
    # Patch the dependency
    with patch("note_gen.routers.utility.get_utility_controller", return_value=mock_controller):
        # Call endpoint
        response = client.get("/")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "Note Generator API"
        assert data["version"] == "1.0.0"
        assert "description" in data
        assert "documentation" in data
        assert "endpoints" in data
        assert "/api/v1/validation" in data["endpoints"]
        assert "/api/v1/import-export" in data["endpoints"]
        mock_controller.get_api_info.assert_called_once()
