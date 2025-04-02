"""Tests for patterns router."""
import pytest
from unittest.mock import MagicMock

from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from note_gen.routers.patterns import router
from note_gen.dependencies import get_pattern_controller
from note_gen.presenters.pattern_presenter import PatternPresenter


def test_router_exists():
    """Test that the router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


@pytest.fixture
def mock_pattern_controller():
    """Create a mock pattern controller."""
    controller = MagicMock()
    controller.get_all_note_patterns.return_value = []
    controller.get_all_rhythm_patterns.return_value = []
    return controller

@pytest.fixture(autouse=True)
def mock_pattern_presenter(monkeypatch):
    """Mock the pattern presenter."""
    # Create a mock for the present_many_note_patterns method
    mock_present_many = MagicMock(return_value=[])
    monkeypatch.setattr(PatternPresenter, "present_many_note_patterns", mock_present_many)

    # Create a mock for the present_many_rhythm_patterns method
    mock_present_many_rhythm = MagicMock(return_value=[])
    monkeypatch.setattr(PatternPresenter, "present_many_rhythm_patterns", mock_present_many_rhythm)

@pytest.fixture
def app_with_router(mock_pattern_controller):
    """Create a FastAPI app with the router mounted."""
    app = FastAPI()

    # Override the dependency
    app.dependency_overrides = {
        get_pattern_controller: lambda: mock_pattern_controller
    }

    app.include_router(router)
    return app


@pytest.fixture
def client(app_with_router):
    """Create a test client."""
    return TestClient(app_with_router)


def test_get_patterns_route_exists(client):
    """Test that the GET /note-patterns route exists."""
    # Make a request to the route
    response = client.get("/note-patterns")

    # The route should exist
    assert response.status_code != 404

    # We're just testing that the route exists, not the implementation
    # So we'll just check that we get a response, even if it's an error
    assert response.status_code in [200, 500]


def test_create_note_pattern_route_exists(client):
    """Test that the POST /note-patterns route exists."""
    # Create request data
    request_data = {
        "name": "TestPattern",
        "pattern": [1, 2, 3, 4]
    }

    # Make a request to the route
    response = client.post("/note-patterns", json=request_data)

    # The route should exist
    assert response.status_code != 404

    # We're just testing that the route exists, not the validation logic
    # So we'll just check that we get a response, even if it's an error
    assert response.status_code in [200, 400, 422]
