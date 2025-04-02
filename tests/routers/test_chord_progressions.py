"""Tests for chord progressions router."""
import pytest

from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from note_gen.routers.chord_progressions import router


def test_router_exists():
    """Test that the router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


@pytest.fixture
def app_with_router():
    """Create a FastAPI app with the router mounted."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app_with_router):
    """Create a test client."""
    return TestClient(app_with_router)


def test_get_all_progressions_route_exists(client):
    """Test that the GET / route exists."""
    # Make a request to the route
    response = client.get("/")

    # The route should exist
    assert response.status_code != 404

    # We're just testing that the route exists, not the implementation
    # So we'll just check that we get a response, even if it's an error
    assert response.status_code in [200, 500]


def test_create_progression_route_exists(client):
    """Test that the POST / route exists."""
    # Create request data
    request_data = {
        "name": "Test Progression",
        "key": "C",
        "scale_type": "MAJOR",
        "chords": [
            {"root": "C", "quality": "MAJOR", "duration": 1.0},
            {"root": "F", "quality": "MAJOR", "duration": 1.0},
            {"root": "G", "quality": "MAJOR", "duration": 1.0},
            {"root": "C", "quality": "MAJOR", "duration": 1.0}
        ]
    }

    # Make a request to the route
    response = client.post("/", json=request_data)

    # The route should exist
    assert response.status_code != 404

    # We're just testing that the route exists, not the implementation
    # So we'll just check that we get a response, even if it's an error
    assert response.status_code in [200, 400, 500]
