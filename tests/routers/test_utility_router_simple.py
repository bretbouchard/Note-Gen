"""Simple tests for the utility router."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from note_gen.routers.utility import router


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


def test_health_check_endpoint_exists(client):
    """Test that the health check endpoint exists."""
    response = client.get("/health")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_get_statistics_endpoint_exists(client):
    """Test that the get statistics endpoint exists."""
    response = client.get("/stats")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_list_all_patterns_endpoint_exists(client):
    """Test that the list all patterns endpoint exists."""
    response = client.get("/patterns-list")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_get_api_info_endpoint_exists(client):
    """Test that the get API info endpoint exists."""
    response = client.get("/")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404
