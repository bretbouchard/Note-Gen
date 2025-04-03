"""Simple tests for the import/export router."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from note_gen.routers.import_export import router


@pytest.fixture
def app():
    """Create a test app with the import/export router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


def test_export_chord_progressions_endpoint_exists(client):
    """Test that the export chord progressions endpoint exists."""
    response = client.get("/export/chord-progressions")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_export_note_patterns_endpoint_exists(client):
    """Test that the export note patterns endpoint exists."""
    response = client.get("/export/note-patterns")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_export_rhythm_patterns_endpoint_exists(client):
    """Test that the export rhythm patterns endpoint exists."""
    response = client.get("/export/rhythm-patterns")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_export_sequences_endpoint_exists(client):
    """Test that the export sequences endpoint exists."""
    response = client.get("/export/sequences")
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_import_chord_progressions_endpoint_exists(client):
    """Test that the import chord progressions endpoint exists."""
    # Create a simple file-like object
    files = {"file": ("test.json", b"{}", "application/json")}
    response = client.post("/import/chord-progressions", files=files)
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_import_note_patterns_endpoint_exists(client):
    """Test that the import note patterns endpoint exists."""
    # Create a simple file-like object
    files = {"file": ("test.json", b"{}", "application/json")}
    response = client.post("/import/note-patterns", files=files)
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_import_rhythm_patterns_endpoint_exists(client):
    """Test that the import rhythm patterns endpoint exists."""
    # Create a simple file-like object
    files = {"file": ("test.json", b"{}", "application/json")}
    response = client.post("/import/rhythm-patterns", files=files)
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404


def test_import_sequences_endpoint_exists(client):
    """Test that the import sequences endpoint exists."""
    # Create a simple file-like object
    files = {"file": ("test.json", b"{}", "application/json")}
    response = client.post("/import/sequences", files=files)
    # We don't care about the response, just that the endpoint exists
    assert response.status_code != 404
