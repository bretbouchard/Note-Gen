# file: tests/api/test_user_routes.py

import os
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from src.note_gen import app
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.models.patterns import RhythmPatternData, RhythmNote
from src.note_gen.database.db import get_db_conn, init_db, close_mongo_connection
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uuid
import httpx
import logging

# Set test environment
os.environ["TESTING"] = "1"

logger = logging.getLogger(__name__)

@pytest.fixture
def rhythm_data():
    """Fixture for valid rhythm pattern data."""
    return {
        "notes": [
            {
                "position": 0.0,
                "duration": 1.0,
                "velocity": 100,
                "is_rest": False
            },
            {
                "position": 1.0,
                "duration": 1.0,
                "velocity": 100,
                "is_rest": True
            }
        ],
        "time_signature": "4/4",
        "swing_ratio": 0.5,
        "default_duration": 1.0,
        "total_duration": 4.0,
        "groove_type": "swing"
    }

@pytest_asyncio.fixture
async def test_client(test_db):
    """
    Provides an async test client specifically for user routes tests.
    Uses test_db fixture from conftest.py to ensure database is properly initialized.
    """
    logger.debug("Creating test client for user routes tests")
    
    # Create transport using the ASGI app
    transport = httpx.ASGITransport(app=app)
    
    # Use http://test as base_url - the actual URL doesn't matter
    # because we're using the transport directly
    async with httpx.AsyncClient(
        transport=transport, 
        base_url="http://test",
        # Explicitly set follow_redirects to True to handle 307 Temporary Redirect responses
        # This is necessary to ensure the test client follows redirects correctly
        follow_redirects=True,  
    ) as client:
        logger.debug("Test client created")
        yield client
    
    logger.debug("Test client closed")

# Consolidated tests for user routes functionality

@pytest.mark.asyncio
async def test_user_routes_functionality(test_client):
    """Test user routes functionality."""
    # Test get user - should return 200 with default test user
    response = await test_client.get('/api/v1/users/me')
    assert response.status_code == 200
    assert response.json() == {"username": "testuser"}

@pytest.mark.asyncio
async def test_get_rhythm_pattern(test_client, rhythm_data):
    """Test getting a rhythm pattern."""
    # Generate a unique name using a timestamp to avoid conflicts with other tests
    unique_name = f"Test Get Pattern {uuid.uuid4()}"
    
    pattern = {
        "name": unique_name,
        "data": rhythm_data,
        "is_test": True,
        "style": "basic",
        "tags": ["test"]
    }
    response = await test_client.post('/api/v1/rhythm-patterns', json=pattern)
    assert response.status_code == 201
    created_pattern = response.json()
    pattern_id = created_pattern["id"]

    # Get pattern
    response = await test_client.get(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200
    assert response.json()["name"] == unique_name

@pytest.mark.asyncio
async def test_invalid_rhythm_pattern_id(test_client):
    """Test getting a rhythm pattern with invalid ID."""
    response = await test_client.get('/api/v1/rhythm-patterns/invalid_id')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_rhythm_pattern(test_client, rhythm_data):
    """Test creating a rhythm pattern."""
    pattern = {
        "name": "Test Create Pattern",
        "data": rhythm_data,
        "is_test": True,
        "style": "basic",
        "tags": ["test"]
    }

    response = await test_client.post('/api/v1/rhythm-patterns', json=pattern)
    assert response.status_code == 201, f"Failed to create pattern: {response.json()}"
    created_pattern = response.json()
    assert created_pattern["name"] == "Test Create Pattern"
    assert created_pattern["data"]["time_signature"] == "4/4"

@pytest.mark.asyncio
async def test_create_duplicate_rhythm_pattern(test_client, rhythm_data):
    """Test creating a duplicate rhythm pattern."""
    # Generate a unique name using a timestamp to avoid conflicts with other tests
    unique_name = f"Test Duplicate Pattern {uuid.uuid4()}"
    
    pattern = {
        "name": unique_name,
        "data": rhythm_data,
        "is_test": True,
        "style": "basic",
        "tags": ["test"]
    }

    # Create first pattern
    response = await test_client.post('/api/v1/rhythm-patterns', json=pattern)
    assert response.status_code == 201, f"Failed to create first pattern: {response.json()}"

    # Try to create duplicate pattern
    response = await test_client.post('/api/v1/rhythm-patterns', json=pattern)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_invalid_rhythm_pattern(test_client):
    """Test creating an invalid rhythm pattern."""
    invalid_pattern = {
        "name": "Invalid Pattern",
        "is_test": True,
        "style": "basic",
        "tags": ["test"]
    }

    response = await test_client.post('/api/v1/rhythm-patterns', json=invalid_pattern)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_and_delete_rhythm_pattern(test_client, rhythm_data):
    """Test creating and deleting a rhythm pattern."""
    # Use a unique name for each test run
    unique_name = f"Test Delete Pattern {uuid.uuid4()}"
    
    pattern = {
        "name": unique_name,
        "data": rhythm_data,
        "is_test": True,
        "style": "basic",
        "tags": ["test"]
    }

    # Create pattern
    response = await test_client.post('/api/v1/rhythm-patterns', json=pattern)
    assert response.status_code == 201, f"Failed to create pattern: {response.text}"
    created_pattern = response.json()
    pattern_id = created_pattern.get("id")
    
    # Ensure we have a valid ID
    assert pattern_id is not None, "Created pattern is missing ID"
    print(f"Created rhythm pattern ID: {pattern_id}")
    
    # Test we can retrieve the pattern first
    response = await test_client.get(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200, f"Failed to retrieve pattern before deletion: {response.text}"

    # Delete the pattern
    response = await test_client.delete(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 204, f"Failed to delete pattern: {response.text}"

    # Verify pattern is deleted
    response = await test_client.get(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 404, f"Pattern still exists after deletion: {response.text}"