"""Test chord progression check endpoints."""
import pytest
from fastapi.testclient import TestClient
from note_gen.main import app  # Update import path

@pytest.fixture
def client():
    return TestClient(app)

# Your test cases here
