import asyncio
import pytest
import pytest_asyncio
import uuid
from src.note_gen.main import app
from httpx import AsyncClient, ASGITransport
from starlette.concurrency import iterate_in_threadpool
from src.note_gen.database.db import get_db_conn, MONGODB_URI
from src.note_gen.dependencies import get_db_conn
from bson import ObjectId
import logging
from src.note_gen.models.fake_scale_info import FakeScaleInfo

logger = logging.getLogger(__name__)

@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Setup test database and cleanup after tests."""
    db = await get_db_conn()
    try:
        # Clear existing data
        await db.chord_progressions.delete_many({})
        
        # Setup test data
        progression = {
            "_id": ObjectId(),
            "name": "Test Base Progression",
            "chords": [
                {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
                {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
                {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
                {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"}
            ],
            'key': 'C',
            'scale_type': 'MAJOR',
            'complexity': 0.5,
            'scale_info': {
                'key': 'C',
                'scale_type': 'MAJOR',
                'notes': ['C', 'D', 'E', 'F', 'G', 'A', 'B']
            }
        }
        await db.chord_progressions.insert_one(progression)
        yield db
    finally:
        # Cleanup after tests
        await db.chord_progressions.delete_many({})

@pytest.mark.asyncio
async def test_chord_progression_functionality(app_client, async_database):
    db = await async_database
    """Test the chord progression creation, retrieval, and deletion functionality."""
    # Test data
    chord_progression_data = {
        "name": "Test Progression",
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "complexity": 0.5,
        "scale_info": {
            "key": "C",
            "scale_type": "MAJOR",
            "notes": ["C", "D", "E", "F", "G", "A", "B"]
        }
    }

    # Create chord progression
    response = await app_client.post("/api/v1/chord-progressions", json=chord_progression_data)
    if response.status_code != 201:
        logger.error(f"Failed to create progression. Status code: {response.status_code}")
        logger.error(f"Response: {response.json()}")
    assert response.status_code == 201, f"Failed to create progression: {response.json()}"
    result = response.json()
    progression_id = result["id"]

    # Get chord progression
    response = await app_client.get(f"/api/v1/chord-progressions/{progression_id}")
    if response.status_code != 200:
        logger.error(f"Failed to get progression. Status code: {response.status_code}")
        logger.error(f"Response: {response.json()}")
    assert response.status_code == 200, f"Failed to get progression: {response.json()}"
    result = response.json()
    assert result["name"] == chord_progression_data["name"]

    # Test invalid ID
    response = await app_client.get("/api/v1/chord-progressions/invalid_id")
    assert response.status_code == 404

    # Delete chord progression
    response = await app_client.delete(f"/api/v1/chord-progressions/{progression_id}")
    if response.status_code != 200:
        logger.error(f"Failed to delete progression. Status code: {response.status_code}")
        logger.error(f"Response: {response.json()}")
    assert response.status_code == 200, f"Failed to delete progression: {response.json()}"
    assert "deleted successfully" in response.json()["message"]

    # Verify deletion
    response = await app_client.get(f"/api/v1/chord-progressions/{progression_id}")
    assert response.status_code == 404

    # Test create duplicate chord progression
    response = await app_client.post("/api/v1/chord-progressions", json=chord_progression_data)
    assert response.status_code == 201  # Should succeed since original was deleted

    # Test create invalid chord progression
    invalid_progression = {
        "name": "Invalid Progression",
        "chords": ["invalid"],  # Invalid chord format
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "key": "C",
            "scale_type": "MAJOR",
            "notes": ["C", "D", "E", "F", "G", "A", "B"]
        }
    }
    response = await app_client.post("/api/v1/chord-progressions", json=invalid_progression)
    assert response.status_code == 422  # Validation error

    # Test create chord progression with missing fields
    missing_fields_progression = {
        "name": "Missing Fields Progression",
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"}
        ]
        # Missing key and scale_type
    }
    response = await app_client.post("/api/v1/chord-progressions", json=missing_fields_progression)
    assert response.status_code == 422  # Validation error

    # Test update chord progression
    update_data = {
        "name": "Updated Test Progression",
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "B", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "D",
        "scale_type": "MAJOR",
        "complexity": 0.7,
        "scale_info": {
            "key": "D",
            "scale_type": "MAJOR",
            "notes": ["D", "E", "F#", "G", "A", "B", "C#"]
        }
    }
    response = await app_client.put(f"/api/v1/chord-progressions/{progression_id}", json=update_data)
    if response.status_code != 200:
        logger.error(f"Failed to update progression. Status code: {response.status_code}")
        logger.error(f"Response: {response.json()}")
    assert response.status_code == 200, f"Failed to update progression: {response.json()}"
    result = response.json()
    assert result["name"] == update_data["name"]
    assert result["key"] == update_data["key"]

    # Test update non-existent chord progression
    fake_id = str(ObjectId())
    response = await app_client.put(f"/api/v1/chord-progressions/{fake_id}", json=update_data)
    assert response.status_code == 404

    # Test delete non-existent chord progression
    response = await app_client.delete(f"/api/v1/chord-progressions/{fake_id}")
    assert response.status_code == 404
