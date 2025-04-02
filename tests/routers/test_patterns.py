"""Tests for patterns router."""
import pytest

from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from note_gen.routers.patterns import router


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


def test_get_patterns_route_exists(client):
    """Test that the GET /note-patterns route exists."""
    # Make a request to the route
    response = client.get("/note-patterns")

    # The route should exist
    assert response.status_code != 404
    assert response.status_code == 200

    # Verify the response structure
    data = response.json()
    assert "patterns" in data
    assert isinstance(data["patterns"], list)


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
