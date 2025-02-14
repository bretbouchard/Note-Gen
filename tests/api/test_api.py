from typing import List, Dict, Any, Optional, AsyncGenerator
from collections.abc import AsyncGenerator as AsyncGeneratorABC
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
import pytest
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.note_gen.models.patterns import NotePattern
from src.note_gen.database.db import MongoDBConnection, init_db, close_mongo_connection
from src.note_gen.dependencies import get_db_conn
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError
from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression, ChordQualityType
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
import asyncio
import logging
import uuid
import os
from main import app

# Set testing environment variable
os.environ['TESTING'] = '1'
os.environ['MONGODB_TEST_URI'] = 'mongodb://localhost:27017/test_note_gen'
os.environ['DATABASE_NAME'] = 'test_note_gen'

@pytest.fixture(scope="function")
async def test_db():
    """Fixture to provide a test database."""
    try:
        await init_db()
        async with get_db_conn() as db:
            # Clear all collections before each test
            collections = await db.list_collection_names()
            for collection in collections:
                await db[collection].delete_many({})
            yield db
    finally:
        await close_mongo_connection()

@pytest.fixture(scope="function")
async def test_client(test_db):
    """Fixture to provide an async test client."""
    async with httpx.AsyncClient(
        app=app,
        base_url="http://test",
        follow_redirects=True
    ) as client:
        yield client

@pytest.fixture(scope="function")
def sync_client(test_db):
    """Fixture to provide a sync test client."""
    with TestClient(app) as client:
        yield client

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.asyncio  # This marks all test functions in the file as async


from typing import List, Dict, Any, Optional
from collections.abc import AsyncIterator

class MockCursor(AsyncIterator[Dict[str, Any]]):
    def __init__(self, items: List[Dict[str, Any]]) -> None:
        self.items = items
        self.current = 0

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.items

    def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        return self

    async def __anext__(self) -> Dict[str, Any]:
        if self.current >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.current]
        self.current += 1
        return item

class MockCollection:
    def __init__(self, items: List[Dict[str, Any]]) -> None:
        self.items = items

    async def find(self, query: Optional[Dict[str, Any]] = None) -> AsyncIterator[Dict[str, Any]]:
        return MockCursor(self.items)

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for item in self.items:
            if item.get('_id') == query.get('_id'):
                return item
        return None

    async def insert_one(self, document: Dict[str, Any]) -> None:
        self.items.append(document)

    async def delete_one(self, query: Dict[str, Any]) -> type('DeleteResult', (), {'deleted_count': int}):
        for i, item in enumerate(self.items):
            if item.get('_id') == query.get('_id'):
                del self.items[i]
                return type('DeleteResult', (), {'deleted_count': 1})()
        return type('DeleteResult', (), {'deleted_count': 0})()


class MockDatabase:
    def __init__(self) -> None:
        # Update chord progressions mock with correct root format
        self.chord_progressions = MockCollection([{
            "_id": "1",
            "name": "Test Progression",
            "chords": [
                {
                    "root": {"note_name": "C", "octave": 4},  
                    "quality": ChordQualityType.MAJOR,
                },
                {
                    "root": {"note_name": "G", "octave": 4},  
                    "quality": ChordQualityType.MAJOR,
                },
                {
                    "root": {"note_name": "A", "octave": 4},  
                    "quality": ChordQualityType.MINOR,
                },
                {
                    "root": {"note_name": "F", "octave": 4},  
                    "quality": ChordQualityType.MAJOR,
                }
            ],
            "scale_info": {
                "root": {"note_name": "C", "octave": 4},
                "scale_type": "MAJOR",
                "intervals": [0, 2, 4, 5, 7, 9, 11]
            },
            "key": "C",
            "scale_type": "MAJOR"
        }])

        # Keep note patterns as is since it's working
        self.note_patterns = MockCollection([{
            "_id": "1",
            "name": "Test Pattern",
            "notes": [
                {
                    "note_name": "C",
                    "duration": 1.0,
                    "velocity": 64,
                    "octave": 4
                },
                {
                    "note_name": "E",
                    "duration": 1.0,
                    "velocity": 64,
                    "octave": 4
                },
                {
                    "note_name": "G",
                    "duration": 1.0,
                    "velocity": 64,
                    "octave": 4
                }
            ],
            "description": "Basic pattern",
            "tags": ["test"]
        }])

        # Keep rhythm patterns as is for now
        self.rhythm_patterns = MockCollection([{
            "id": "1",
            "name": "Test Rhythm",
            "pattern": "4 4",  # Simple quarter note pattern
            "description": "Basic rhythm",
            "tags": ["test"],
            "complexity": 1.0,
            "data": {
                "notes": [
                    {
                        "position": 0.0,
                        "duration": 1.0,
                        "velocity": 100,
                        "is_rest": False,
                        "accent": None,
                        "swing_ratio": None
                    },
                    {
                        "position": 1.0,
                        "duration": 1.0,
                        "velocity": 100,
                        "is_rest": False,
                        "accent": None,
                        "swing_ratio": None
                    }
                ],
                "time_signature": "4/4",
                "swing_enabled": False,
                "humanize_amount": 0.0,
                "swing_ratio": 0.67,
                "default_duration": 1.0,
                "total_duration": 2.0,
                "accent_pattern": [],
                "groove_type": "straight",
                "variation_probability": 0.0,
                "duration": 2.0,
                "style": "basic"
            },
            "style": "basic",
            "is_test": True
        }])


@pytest.fixture(autouse=True)
async def setup_teardown(test_db):
    """Setup and teardown for each test."""
    # Setup
    try:
        yield
    finally:
        # Teardown
        try:
            pass
        except Exception as e:
            logger.error(f"Error during teardown: {str(e)}")


# Consolidated tests for API functionality

@pytest.mark.asyncio
async def test_api_functionality(test_client: httpx.AsyncClient) -> None:
    """Test basic API functionality."""
    # Test creating a note pattern
    note_pattern_data = {
        "name": "Test Pattern " + str(uuid.uuid4()),  # Add unique identifier
        "pattern": [0, 4, 7],  # Adding the required pattern field
        "direction": "up",
        "description": "Test pattern",
        "tags": ["test"],
        "is_test": True,
        "duration": 1.0,
        "velocity": 64
    }
    
    response = await test_client.post("/api/v1/note-patterns/", json=note_pattern_data)
    assert response.status_code == 201, f"Failed to create note pattern: {response.text}"
    created_pattern = response.json()
    note_pattern_id = created_pattern["id"]  # Using 'id' instead of '_id'

    # Test get note pattern by id
    response = await test_client.get(f"/api/v1/note-patterns/{note_pattern_id}")
    assert response.status_code == 200
    retrieved_pattern = response.json()
    assert retrieved_pattern["name"] == note_pattern_data["name"]

    # Test update note pattern
    update_data = {
        "name": "Updated Pattern " + str(uuid.uuid4()),
        "pattern": [0, 4, 7],
        "direction": "up",
        "description": "Updated pattern",
        "tags": ["test", "updated"],
        "is_test": True,
        "duration": 1.0,
        "velocity": 64
    }
    response = await test_client.put(f"/api/v1/note-patterns/{note_pattern_id}", json=update_data)
    assert response.status_code == 200
    updated_pattern = response.json()
    assert updated_pattern["name"] == update_data["name"]

    # Test delete note pattern
    response = await test_client.delete(f"/api/v1/note-patterns/{note_pattern_id}")
    assert response.status_code == 204
    assert response.content == b''  # No content for 204 response

    # Test creating a rhythm pattern
    rhythm_pattern_data = {
        "name": "Test Rhythm " + str(uuid.uuid4()),  # Add unique identifier
        "data": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "is_rest": False,
                    "swing_ratio": 0.67
                }
            ],
            "time_signature": "4/4",
            "swing_enabled": False,
            "humanize_amount": 0.0,
            "swing_ratio": 0.67,
            "default_duration": 1.0,
            "total_duration": 4.0,
            "accent_pattern": [],
            "groove_type": "straight",
            "variation_probability": 0.0,
            "duration": 1.0,
            "style": "basic"
        },
        "description": "Test rhythm",
        "tags": ["test"],
        "complexity": 1.0,
        "style": "basic",
        "pattern": "4 4",  # Changed from [4, 4] to "4 4"
        "groove_type": "straight",
        "swing_ratio": 0.67,
        "duration": 1.0
    }
    
    response = await test_client.post("/api/v1/rhythm-patterns/", json=rhythm_pattern_data)
    assert response.status_code == 201, f"Failed to create rhythm pattern: {response.text}"

    # Test creating a chord progression
    chord_progression_data = {
        "name": "Test Progression " + str(uuid.uuid4()),  # Add unique identifier
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": "MAJOR"
            },
            {
                "root": {"note_name": "G", "octave": 4},
                "quality": "MAJOR"
            },
            {
                "root": {"note_name": "A", "octave": 4},
                "quality": "MINOR"
            }
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]  # Major scale intervals
        }
    }
    
    response = await test_client.post("/api/v1/chord-progressions/", json=chord_progression_data)
    assert response.status_code == 201, f"Failed to create chord progression: {response.text}"

    # Test get note patterns
    response = await test_client.get("/api/v1/note-patterns/")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get rhythm patterns
    response = await test_client.get("/api/v1/rhythm-patterns/")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get chord progressions
    response = await test_client.get("/api/v1/chord-progressions/")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get note pattern by id
    response = await test_client.get("/api/v1/note-patterns/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Pattern"

    # Test update note pattern
    update_data = {
        "name": "Updated Pattern " + str(uuid.uuid4()),  # Add unique identifier
        "notes": [
            {
                "note_name": "C",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            },
            {
                "note_name": "E",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            },
            {
                "note_name": "G",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            }
        ],
        "description": "Updated pattern",
        "tags": ["test", "updated"]
    }
    response = await test_client.put("/api/v1/note-patterns/1", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == update_data["name"]

    # Test delete note pattern
    response = await test_client.delete("/api/v1/note-patterns/1")
    assert response.status_code == 204
    assert response.content == b''  # No content for 204 response

    # Test get rhythm pattern by id
    response = await test_client.get("/api/v1/rhythm-patterns/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Rhythm"

    # Test update rhythm pattern
    update_data = {
        "name": "Updated Rhythm " + str(uuid.uuid4()),  # Add unique identifier
        "pattern": "1 1",
        "description": "Updated rhythm",
        "tags": ["test", "updated"]
    }
    response = await test_client.put("/api/v1/rhythm-patterns/1", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == update_data["name"]

    # Test delete rhythm pattern
    response = await test_client.delete("/api/v1/rhythm-patterns/1")
    assert response.status_code == 204
    assert response.content == b''  # No content for 204 response


import pytest
from fastapi import HTTPException
from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression, ChordQualityType

# Test invalid Note creation
async def test_invalid_note_name() -> None:
    with pytest.raises(ValueError) as excinfo:  
        Note(note_name='InvalidNote', octave=4, duration=1.0, velocity=64)  
    assert 'Invalid note name format' in str(excinfo.value)

# Test invalid octave separately
async def test_invalid_note_octave() -> None:
    with pytest.raises(ValueError) as excinfo:
        Note(note_name='C', octave=10, duration=1.0, velocity=64)
    assert 'Invalid octave' in str(excinfo.value)

# Test invalid ChordProgression creation
async def test_invalid_chord_progression_creation() -> None:
    from src.note_gen.models.chord import Chord
    from src.note_gen.models.scale_info import ScaleInfo

    # Test with empty chords list - should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        ChordProgression(
            name='Invalid Progression',
            chords=[],  # Empty list
            key='C',
            scale_type='MAJOR',
            scale_info=ScaleInfo(root=Note(note_name='C', octave=4), scale_type='MAJOR')
        )
    assert "Chords list cannot be empty" in str(excinfo.value)

# Test API endpoint with valid data
async def test_create_chord_progression_valid_data(test_client: httpx.AsyncClient):
    """Test creating a chord progression with valid data."""
    # Create a unique name for the test
    test_name = f"Test Progression {uuid.uuid4()}"
    
    # Prepare test data with proper enum values
    data = {
        "name": test_name,
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": ChordQualityType.MAJOR.value,  # Use enum value
                "notes": [
                    {"note_name": "C", "octave": 4},
                    {"note_name": "E", "octave": 4},
                    {"note_name": "G", "octave": 4}
                ]
            }
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    
    try:
        logger.info("Starting test for creating a chord progression with valid data...")
        response = await test_client.post("/api/v1/chord-progressions/", json=data)
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == test_name
        assert len(response_data["chords"]) == 1
        assert response_data["key"] == "C"
        assert response_data["scale_type"] == "MAJOR"
        
    except Exception as e:
        raise

# Test API endpoint with invalid data
@pytest.mark.asyncio
async def test_create_chord_progression_invalid_data(test_client: httpx.AsyncClient):
    """Test creating a chord progression with invalid data."""
    # Test missing required fields
    invalid_data = {
        "name": "Invalid Progression",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": "MAJOR"
            }
        ],
        "key": "C",
        "scale_type": "MAJOR"
        # Missing required scale_info field
    }
    response = await test_client.post("/api/v1/chord-progressions/", json=invalid_data)
    assert response.status_code == 422, f"Expected validation error, got: {response.text}"

    # Test invalid chord quality
    invalid_quality_data = {
        "name": "Invalid Quality",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": "INVALID_QUALITY"  # Invalid quality value
            }
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    response = await test_client.post("/api/v1/chord-progressions/", json=invalid_quality_data)
    assert response.status_code == 422, f"Expected validation error for invalid quality, got: {response.text}"

    # Test invalid root note
    invalid_root_data = {
        "name": "Invalid Root",
        "chords": [
            {
                "root": {"note_name": "H", "octave": 4},  # H is not a valid note name
                "quality": "MAJOR"
            }
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    response = await test_client.post("/api/v1/chord-progressions/", json=invalid_root_data)
    assert response.status_code == 422, f"Expected validation error for invalid root note, got: {response.text}"
