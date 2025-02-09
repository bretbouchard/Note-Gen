# file: tests/api/test_user_routes.py

import os
import pytest
from fastapi.testclient import TestClient
from main import app
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from src.note_gen.database import get_db, init_db, close_mongo_connection
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uuid

# Set test environment
os.environ["TESTING"] = "1"

@pytest.fixture(autouse=True)
async def setup_and_cleanup():
    """Set up test database and clean up after tests."""
    # Initialize test database
    db = await init_db()
    yield
    # Clean up after test
    await db.rhythm_patterns.delete_many({"is_test": True})
    await close_mongo_connection()

@pytest.fixture
async def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def rhythm_data():
    """Create a consistent rhythm pattern data fixture."""
    # Create four quarter notes at positions 0, 1, 2, and 3
    rhythm_notes = [
        RhythmNote(position=float(i), duration=1.0, velocity=100, is_rest=False)
        for i in range(4)
    ]
    return RhythmPatternData(
        notes=rhythm_notes,
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,  # Each quarter note is 1.0 beats
        total_duration=4.0,    # Total measure duration is 4.0 beats
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=4.0,
        style="basic"
    )

# Consolidated tests for user routes functionality

@pytest.mark.asyncio
async def test_user_routes_functionality(client):
    # Test get user
    response = client.get('/api/v1/users/me')
    assert response.status_code == 200
    
    # Test get user by id - should return 404 since user doesn't exist
    response = client.get('/api/v1/users/1')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_rhythm_pattern(client, rhythm_data):
    # Create a valid rhythm pattern
    pattern = RhythmPattern(
        name="Test Get Pattern",
        data=rhythm_data,
        pattern="4 4",
        description="Basic quarter note pattern",
        tags=["basic"],
        complexity=1.0,
        is_test=True
    )

    # Create the pattern
    response = client.post('/api/v1/rhythm-patterns', json=pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    pattern_id = created_pattern["id"]

    # Get the pattern by ID
    response = client.get(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 200
    retrieved_pattern = response.json()
    assert retrieved_pattern["name"] == "Test Get Pattern"

@pytest.mark.asyncio
async def test_invalid_rhythm_pattern_id(client):
    response = client.get('/api/v1/rhythm-patterns/invalid_id')
    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid rhythm pattern ID format"

@pytest.mark.asyncio
async def test_create_rhythm_pattern(client, rhythm_data):
    pattern = RhythmPattern(
        name="Test Create Pattern",
        data=rhythm_data,
        pattern="4 4 4 4",  # Four quarter notes to fill a 4/4 measure
        description="Basic quarter note pattern",
        tags=["basic"],
        complexity=1.0,
        is_test=True
    )

    response = client.post('/api/v1/rhythm-patterns', json=pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    assert created_pattern["name"] == "Test Create Pattern"
    assert created_pattern["id"] is not None

@pytest.mark.asyncio
async def test_create_duplicate_rhythm_pattern(client, rhythm_data):
    pattern = RhythmPattern(
        name="Test Duplicate Pattern",
        data=rhythm_data,
        pattern="4 4 4 4",  # Four quarter notes to fill a 4/4 measure
        description="Basic quarter note pattern",
        tags=["basic"],
        complexity=1.0,
        is_test=True
    )

    # Create first pattern
    response = client.post('/api/v1/rhythm-patterns', json=pattern.model_dump())
    print(f"Pattern data: {pattern.model_dump()}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201

    # Try to create duplicate pattern
    response = client.post('/api/v1/rhythm-patterns', json=pattern.model_dump())
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_invalid_rhythm_pattern(client):
    # Create an invalid pattern missing required fields
    invalid_pattern = {
        "name": "Invalid Pattern",
        "pattern": "4 4"
    }

    response = client.post('/api/v1/rhythm-patterns', json=invalid_pattern)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_and_delete_rhythm_pattern(client, rhythm_data):
    pattern = RhythmPattern(
        name="Test Delete Pattern",
        data=rhythm_data,
        pattern="4 4",
        description="Basic quarter note pattern",
        tags=["basic"],
        complexity=1.0,
        is_test=True
    )

    # Create pattern
    response = client.post('/api/v1/rhythm-patterns', json=pattern.model_dump())
    assert response.status_code == 201
    created_pattern = response.json()
    pattern_id = created_pattern["id"]

    # Delete the pattern
    response = client.delete(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 204

    # Verify pattern is deleted
    response = client.get(f'/api/v1/rhythm-patterns/{pattern_id}')
    assert response.status_code == 404