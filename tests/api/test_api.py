from typing import List, Dict, Any, Optional, AsyncGenerator
from collections.abc import AsyncGenerator as AsyncGeneratorABC

from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.note_gen.models.patterns import NotePattern
from src.note_gen.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import ValidationError
from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression, ChordQualityType
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
import asyncio
import logging

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
        # Simulate asynchronous behavior
        logger.info("Accessing MongoDB for test operations...")
        return MockCursor(self.items)

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Simulate asynchronous behavior
        logger.info("Accessing MongoDB for test operations...")
        for item in self.items:
            if item.get('_id') == query.get('_id'):
                return item
        return None

    async def insert_one(self, document: Dict[str, Any]) -> None:
        # Simulate asynchronous behavior
        logger.info("Accessing MongoDB for test operations...")
        self.items.append(document)


class MockDatabase:
    def __init__(self) -> None:
        # Update chord progressions mock with correct root format
        self.chord_progressions = MockCollection([{
            "_id": "1",
            "name": "Test Progression",
            "chords": [
                {
                    "name": "C",
                    "root": {"note_name": "C", "octave": 4},  # Root as dictionary
                    "quality": ChordQualityType.MAJOR,
                    "intervals": [0, 4, 7]
                },
                {
                    "name": "G",
                    "root": {"note_name": "G", "octave": 4},  # Root as dictionary
                    "quality": ChordQualityType.MAJOR,
                    "intervals": [0, 4, 7]
                },
                {
                    "name": "Am",
                    "root": {"note_name": "A", "octave": 4},  # Root as dictionary
                    "quality": ChordQualityType.MINOR,
                    "intervals": [0, 3, 7]
                },
                {
                    "name": "F",
                    "root": {"note_name": "F", "octave": 4},  # Root as dictionary
                    "quality": ChordQualityType.MAJOR,
                    "intervals": [0, 4, 7]
                }
            ],
            "scale_info": {
                "root": Note(note_name='C', octave=4),
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


from main import app
from httpx import AsyncClient, ASGITransport

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    mock_db = MockDatabase()
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client

# Consolidated tests for API functionality

@pytest.mark.asyncio
async def test_api_functionality(client: AsyncClient) -> None:
    """Test basic API functionality."""
    logger.info("Accessing MongoDB for test operations...")
    # Test creating a note pattern
    note_pattern_data = {
        "name": "Test Pattern",
        "pattern": [0, 4, 7],  # Adding the required pattern field
        "notes": [
            {
                "note_name": "C",
                "duration": 1.0,
                "velocity": 64,
                "octave": 4
            }
        ],
        "description": "Test pattern",
        "tags": ["test"],
        "pattern_type": "basic"
    }
    
    response = await client.post("/api/v1/note-patterns/", json=note_pattern_data)
    assert response.status_code == 201, f"Failed to create note pattern: {response.text}"

    # Test creating a rhythm pattern
    rhythm_pattern_data = {
        "name": "Test Rhythm",
        "pattern": "4 4",
        "description": "Test rhythm",
        "tags": ["test"],
        "data": {
            "notes": [
                {
                    "position": 0.0,
                    "duration": 1.0,
                    "velocity": 100,
                    "is_rest": False
                }
            ],
            "time_signature": "4/4"
        }
    }
    
    response = await client.post("/api/v1/rhythm-patterns/", json=rhythm_pattern_data)
    assert response.status_code == 201, f"Failed to create rhythm pattern: {response.text}"

    # Test creating a chord progression
    chord_progression_data = {
        "name": "Test Progression",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": "MAJOR"
            }
        ],
        "key": "C",
        "scale_type": "MAJOR"
    }
    
    response = await client.post("/api/v1/chord-progressions/", json=chord_progression_data)
    assert response.status_code == 201, f"Failed to create chord progression: {response.text}"

    # Test get note patterns
    response = await client.get("/api/v1/note-patterns/")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get rhythm patterns
    response = await client.get("/api/v1/rhythm-patterns/")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get chord progressions
    response = await client.get("/api/v1/chord-progressions/")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Test get note pattern by id
    response = await client.get("/api/v1/note-patterns/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Pattern"

    # Test update note pattern
    update_data = {
        "name": "Updated Pattern",
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
    response = await client.put("/api/v1/note-patterns/1", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "Updated Pattern"

    # Test delete note pattern
    response = await client.delete("/api/v1/note-patterns/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Note pattern deleted successfully"

    # Test get rhythm pattern by id
    response = await client.get("/api/v1/rhythm-patterns/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Rhythm"

    # Test update rhythm pattern
    update_data = {
        "name": "Updated Rhythm",
        "pattern": "1 1",
        "description": "Updated rhythm",
        "tags": ["test", "updated"]
    }
    response = await client.put("/api/v1/rhythm-patterns/1", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == "Updated Rhythm"

    # Test delete rhythm pattern
    response = await client.delete("/api/v1/rhythm-patterns/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Rhythm pattern deleted successfully"


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
async def test_create_chord_progression_valid_data(client: AsyncClient):
    """Test creating a chord progression with valid data."""
    logger.info("Starting test for creating a chord progression with valid data...")
    data = {
        "name": "Test Progression",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 100},
                "quality": "MAJOR",
                "notes": [],
                "inversion": 0
            }
        ],
        "key": "C",
        "scale_type": "MAJOR"
    }
    logger.info("Sending data to create chord progression: %s", data)
    response = await client.post("/api/v1/chord-progressions/", json=data)
    logger.info("Received response with status code: %d", response.status_code)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == "Test Progression"
    assert len(response_data["chords"]) == 1
    assert response_data["key"] == "C"
    assert response_data["scale_type"] == "MAJOR"

# Test API endpoint with invalid data
async def test_create_chord_progression_invalid_data(client: AsyncClient):
    """Test creating a chord progression with invalid data."""
    data = {
        "name": "Invalid Progression",
        "chords": [],  # Invalid: empty chords list
        "key": "C",
        "scale_type": "MAJOR"
    }
    
    response = await client.post("/api/v1/chord-progressions/", json=data)
    assert response.status_code == 422
