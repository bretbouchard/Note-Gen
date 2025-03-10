# file: tests/api/test_user_routes.py

import os
import pytest
from fastapi.testclient import TestClient
from main import app
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
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

@pytest.fixture
async def test_db():
    """Fixture to provide a test database connection."""
    logger.debug(f'Connecting to database with MONGODB_URI: {os.getenv("MONGODB_URI")}, db_name: test_note_gen')
    async with get_db_conn() as db:
        if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
            collections = await db.list_collection_names()
            for collection in collections:
                await db[collection].delete_many({})
        yield db

@pytest.fixture
async def test_client():
    """Fixture to provide an async test client."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        yield client

# Consolidated tests for user routes functionality

@pytest.mark.asyncio
async def test_user_routes_functionality(test_client):
    """Test user routes functionality."""
    # Test get user - should return 404 since no user exists
    response = await test_client.get('/api/v1/users/me')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_rhythm_pattern(test_client, rhythm_data):
    """Test getting a rhythm pattern."""
    pattern = {
        "name": "Test Get Pattern",
        "data": rhythm_data,
        "is_test": True,
        "style": "basic",
        "tags": ["test"]
    }
    response = await test_client.post('/api/v1/rhythm-patterns', json=pattern)
    assert response.status_code == 201

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
    pattern = {
        "name": "Test Duplicate Pattern",
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
    pattern = {
        "name": "Test Delete Pattern",
        "data": rhythm_data,
        "is_test": True,
        "style": "basic",
        "tags": ["test"]
    }

    # Create pattern
    response = await test_client.post('/api/v1/rhythm-patterns', json=pattern)
    assert response.status_code == 201, f"Failed to create pattern: {response.json()}"
    created_pattern = response.json()
    pattern_id = created_pattern["id"]

    # Delete the pattern
    response = await test_client.delete(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 204

    # Verify pattern is deleted
    response = await test_client.get(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 404