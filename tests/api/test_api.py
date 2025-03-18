from typing import List, Dict, Any, Optional, AsyncGenerator
from collections.abc import AsyncGenerator as AsyncGeneratorABC
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
import pytest
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.note_gen.models.patterns import NotePattern
from src.note_gen.database.db import init_db, close_mongo_connection
from src.note_gen.dependencies import get_db_conn
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.patterns import ChordProgression, RhythmPattern, RhythmPatternData, RhythmNote
import asyncio
import logging
import uuid
import os
from main import app
import time

# Set testing environment variable
os.environ['TESTING'] = '1'
os.environ['MONGODB_TEST_URI'] = 'mongodb://localhost:27017/test_note_gen'
os.environ['DATABASE_NAME'] = 'test_note_gen'

@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Fixture to provide a test database."""
    try:
        await init_db()
        db = await get_db_conn()
        yield db
    finally:
        await close_mongo_connection()

@pytest.fixture(scope="function")
async def test_client(test_db):
    """Fixture to provide an async test client."""
    # Add trailing slash handling
    app.middleware_stack = None  # Reset middleware to handle redirects
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, 
        base_url="http://localhost:8000",
        follow_redirects=True  # Add this to follow redirects
    ) as client:
        yield client

@pytest.fixture(scope="function")
def sync_client(test_db):
    """Fixture to provide a sync test client."""
    with TestClient(app, follow_redirects=True) as client:  # Add follow_redirects here too
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
                    "quality": "DOMINANT",  # Use string instead of enum
                },
                {
                    "root": {"note_name": "G", "octave": 4},  
                    "quality": "MAJOR",  # Use string instead of enum
                },
                {
                    "root": {"note_name": "A", "octave": 4},  
                    "quality": "MINOR",  # Use string instead of enum
                },
                {
                    "root": {"note_name": "F", "octave": 4},  
                    "quality": "MAJOR",  # Use string instead of enum
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

    async def __call__(self):
        return self

@pytest.fixture(scope="function")
async def setup_teardown(test_db):
    """Setup and teardown for each test."""
    # Setup
    db = MockDatabase()
    
    # Run the test
    yield db
    
    # Teardown - clear all collections
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        collections = await test_db.list_collection_names()
        for collection in collections:
            await test_db[collection].delete_many({})

@pytest.mark.asyncio
async def test_api_functionality(test_client: httpx.AsyncClient):
    # First ensure we have test data in the database
    db = await get_db_conn()
    db = await db  # Await the coroutine
    
    # Create test data if needed
    test_progression = {
        "name": "Test Progression",
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    
    response = await test_client.post("/api/v1/chord-progressions/create", json=test_progression)
    assert response.status_code == 201
    
    # Now test getting the progression
    response = await test_client.get("/api/v1/chord-progressions")
    assert response.status_code == 200

    # Test GET /api/v1/patterns
    response = await test_client.get("/api/v1/patterns")  # Remove trailing slash
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Test GET /api/v1/note-patterns
    response = await test_client.get("/api/v1/note-patterns")  # Remove trailing slash
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Test GET /api/v1/rhythm-patterns
    response = await test_client.get("/api/v1/rhythm-patterns")  # Remove trailing slash
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Test POST /api/v1/chord-progressions/ with valid data including DOMINANT quality
    valid_chord_progression = {
        "name": f"Test Progression {int(time.time())}",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4, "velocity": 100, "duration": 1},  # Pass as a dictionary
                "quality": "DOMINANT"  # Use string instead of enum
            },
            {
                "root": {"note_name": "G", "octave": 4, "velocity": 100, "duration": 1},  # Pass as a dictionary
                "quality": "MAJOR"  # Use string instead of enum
            }
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4, "velocity": 100, "duration": 1},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    logger.debug(f"Testing POST with valid chord progression: {valid_chord_progression}")
    response = await test_client.post("/api/v1/chord-progressions/create", json=valid_chord_progression)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == f"Test Progression {int(time.time())}"
    assert len(data["chords"]) == 2
    assert data["chords"][0]["root"]["note_name"] == "C"
    assert data["chords"][1]["root"]["note_name"] == "G"

    # Test POST /api/v1/note-patterns/ with valid data
    valid_note_pattern = {
        "name": "Test Pattern",
        "notes": [
            {
                "note_name": "C",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            }
        ],
        "description": "Test pattern",
        "tags": ["test"]
    }
    response = await test_client.post("/api/v1/note-patterns/", json=valid_note_pattern)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Pattern"

    # Test POST /api/v1/rhythm-patterns/ with valid data
    valid_rhythm_pattern = {
        "name": "Test Rhythm",
        "pattern": "4 4",
        "description": "Test rhythm",
        "tags": ["test"],
        "complexity": 1.0,
        "data": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "is_rest": False
                }
            ],
            "time_signature": "4/4",
            "swing_enabled": False,
            "humanize_amount": 0.0,
            "default_duration": 1.0,
            "total_duration": 1.0,
            "accent_pattern": [],
            "groove_type": "straight",
            "variation_probability": 0.0
        },
        "style": "basic"
    }
    response = await test_client.post("/api/v1/rhythm-patterns/", json=valid_rhythm_pattern)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Rhythm"

def test_invalid_note_name():
    with pytest.raises(ValidationError, match="Invalid note name: H"):
        Note(note_name="H", octave=4, duration=1.0, velocity=64)

def test_invalid_note_octave():
    with pytest.raises(ValidationError, match="Input should be less than or equal to 8"):
        Note(note_name="C", octave=11, duration=1.0, velocity=64)

@pytest.mark.asyncio
async def test_create_chord_progression_valid_data(test_client: httpx.AsyncClient) -> None:
    logger.debug(f'CLEAR_DB_AFTER_TESTS value: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        logger.debug('Clearing database after tests')
        db = await get_db_conn()
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})

    valid_chord_progression = {
        "name": f"Test Progression {int(time.time())}",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4, "velocity": 100, "duration": 1},  # Pass as a dictionary
                "quality": "DOMINANT"  # Use string instead of enum
            },
            {
                "root": {"note_name": "G", "octave": 4, "velocity": 100, "duration": 1},
                "quality": "MAJOR"  # Use string instead of enum
            }
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4, "velocity": 100, "duration": 1},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    logger.debug(f"Testing POST with valid chord progression: {valid_chord_progression}")
    response = await test_client.post("/api/v1/chord-progressions/create", json=valid_chord_progression)
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response body: {response.text}")
    if response.status_code != 201:
        logger.error(f"Error response: {response.text}")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == f"Test Progression {int(time.time())}"
    assert len(data["chords"]) == 2
    assert data["chords"][0]["root"]["note_name"] == "C"
    assert data["chords"][1]["root"]["note_name"] == "G"

@pytest.mark.asyncio
async def test_create_chord_progression_invalid_data(test_client: httpx.AsyncClient) -> None:
    logger.debug(f'CLEAR_DB_AFTER_TESTS value: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        logger.debug('Clearing database after tests')
        db = await get_db_conn()
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})

    # Test with missing required fields
    invalid_data_missing_fields = {
        "name": "Test Progression"
        # Missing chords and scale_info
    }
    
    response = await test_client.post("/api/v1/chord-progressions/create", json=invalid_data_missing_fields)
    
    assert response.status_code == 422
    
    # Test with invalid chord quality
    invalid_data_wrong_quality = {
        "name": "Test Progression",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": "INVALID_QUALITY"  # Invalid quality
            }
        ],
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    
    response = await test_client.post("/api/v1/chord-progressions/create", json=invalid_data_wrong_quality)
    
    assert response.status_code == 422
    
    # Test with invalid note name
    invalid_data_wrong_note = {
        "name": "Test Progression",
        "chords": [
            {
                "root": {"note_name": "H", "octave": 4},  # H is not a valid note name
                "quality": "MAJOR"  # Use string instead of enum
            }
        ],
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    
    response = await test_client.post("/api/v1/chord-progressions/create", json=invalid_data_wrong_note)
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_chord_progression_valid_data_with_additional_fields(test_client: httpx.AsyncClient) -> None:
    logger.debug(f'CLEAR_DB_AFTER_TESTS value: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        logger.debug('Clearing database after tests')
        db = await get_db_conn()
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})

    valid_chord_progression = {
        "name": f"Test Progression {int(time.time())}",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4, "velocity": 100, "duration": 1},
                "quality": "DOMINANT"  # Use string instead of enum
            },
            {
                "root": {"note_name": "G", "octave": 4, "velocity": 100, "duration": 1},
                "quality": "MAJOR"  # Use string instead of enum
            }
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4, "velocity": 100, "duration": 1},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        },
        "additional_field": "test"  # Additional field
    }
    logger.debug(f"Testing POST with valid chord progression: {valid_chord_progression}")
    response = await test_client.post("/api/v1/chord-progressions/create", json=valid_chord_progression)
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response body: {response.text}")
    if response.status_code != 201:
        logger.error(f"Error response: {response.text}")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == f"Test Progression {int(time.time())}"
    assert len(data["chords"]) == 2
    assert data["chords"][0]["root"]["note_name"] == "C"
    assert data["chords"][1]["root"]["note_name"] == "G"

@pytest.mark.asyncio
async def test_create_chord_progression_invalid_data_with_missing_chords(test_client: httpx.AsyncClient) -> None:
    logger.debug(f'CLEAR_DB_AFTER_TESTS value: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        logger.debug('Clearing database after tests')
        db = await get_db_conn()
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})

    invalid_data_missing_chords = {
        "name": "Test Progression",
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    logger.debug(f"Testing POST with invalid chord progression: {invalid_data_missing_chords}")
    response = await test_client.post("/api/v1/chord-progressions/create", json=invalid_data_missing_chords)
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response body: {response.text}")
    if response.status_code != 422:
        logger.error(f"Error response: {response.text}")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_chord_progression_invalid_data_with_empty_chords(test_client: httpx.AsyncClient) -> None:
    logger.debug(f'CLEAR_DB_AFTER_TESTS value: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
    if os.getenv("CLEAR_DB_AFTER_TESTS", "0") == "1":
        logger.debug('Clearing database after tests')
        db = await get_db_conn()
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})

    invalid_data_empty_chords = {
        "name": "Test Progression",
        "chords": [],
        "key": "C",
        "scale_type": "MAJOR",
        "scale_info": {
            "root": {"note_name": "C", "octave": 4},
            "scale_type": "MAJOR",
            "intervals": [0, 2, 4, 5, 7, 9, 11]
        }
    }
    logger.debug(f"Testing POST with invalid chord progression: {invalid_data_empty_chords}")
    response = await test_client.post("/api/v1/chord-progressions/create", json=invalid_data_empty_chords)
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response body: {response.text}")
    if response.status_code != 422:
        logger.error(f"Error response: {response.text}")
    assert response.status_code == 422
