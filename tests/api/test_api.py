"""API endpoint tests."""
import os
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.note_gen.api.main import app
from src.note_gen.api.database import get_db

# Create test client
client = TestClient(app)

# Create a test database client
test_client = AsyncIOMotorClient("mongodb://localhost:27017")
test_db = test_client["note_gen_db_dev"]

# Override database dependency for testing
async def override_get_db():
    """Override database connection for testing."""
    return test_db

app.dependency_overrides[get_db] = override_get_db

def test_read_main():
    """Test main endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Note Generator API"}

@pytest.mark.asyncio
async def test_get_patterns():
    """Test patterns endpoint."""
    response = client.get("/api/v1/patterns")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_pattern_by_id():
    """Test getting pattern by ID."""
    response = client.get("/api/v1/patterns/test_id")
    assert response.status_code in (200, 404)
