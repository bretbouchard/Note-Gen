"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from src.note_gen.main import app

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)
