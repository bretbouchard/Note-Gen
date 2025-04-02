"""Tests for chord progressions router."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from src.note_gen.routers.chord_progressions import router


def test_router_exists():
    """Test that the router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


@pytest.fixture
def app_with_router():
    """Create a FastAPI app with the router mounted."""
    app = FastAPI()
    app.include_router(router, prefix="/chord-progressions", tags=["chord-progressions"])
    return app


@pytest.fixture
def client(app_with_router):
    """Create a test client."""
    return TestClient(app_with_router)


def test_get_all_progressions_route_exists(client):
    """Test that the GET /chord-progressions route exists."""
    # Make a request to the route
    response = client.get("/chord-progressions")
    
    # The route should exist
    assert response.status_code != 404
    assert response.status_code == 200
    
    # Verify the response structure
    data = response.json()
    assert "progressions" in data
    assert isinstance(data["progressions"], list)


def test_create_progression_route_exists(client):
    """Test that the POST /chord-progressions route exists."""
    # Create request data
    request_data = [
        {"root": "C", "quality": "MAJOR", "duration": 1.0},
        {"root": "F", "quality": "MAJOR", "duration": 1.0},
        {"root": "G", "quality": "MAJOR", "duration": 1.0},
        {"root": "C", "quality": "MAJOR", "duration": 1.0}
    ]
    
    # Make a request to the route
    response = client.post("/chord-progressions", json=request_data)
    
    # The route should exist
    assert response.status_code != 404
    
    # Verify the response structure
    data = response.json()
    assert "progression_id" in data
