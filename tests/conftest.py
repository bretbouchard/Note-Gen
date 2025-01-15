import asyncio
import atexit
import logging
import os
import sys
import threading
import uuid
from typing import Any, AsyncGenerator, Generator

import mongomock
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database

# from src.note_gen.main import app
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.populate_db import format_chord_progression, format_note_pattern, format_rhythm_pattern

# Configuration
MONGO_URL = "mongodb://localhost:27017/"

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Set up logging
logger = logging.getLogger(__name__)

# Create MongoDB clients for testing
client: MongoClient = MongoClient(MONGO_URL)
mock_client: mongomock.MongoClient = mongomock.MongoClient()

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Create a FastAPI test client."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    """Create a test database using motor."""
    client = AsyncIOMotorClient[Any](MONGO_URL)
    db_name = f"test_db_{uuid.uuid4().hex}"
    db = client[db_name]
    yield db
    await client.drop_database(db_name)
    client.close()

@pytest.fixture(scope="session")
def mock_db() -> Generator[Database[Any], None, None]:
    """Create a mock MongoDB database."""
    mock_client: mongomock.MongoClient = mongomock.MongoClient()
    db = mock_client.db
    yield db
    mock_client.close()

@pytest.fixture(scope="function")
async def setup_database(test_db: AsyncIOMotorDatabase[Any]) -> AsyncGenerator[None, None]:
    """Set up the test database with sample data."""
    # Sample data
    chord_progressions = [
        format_chord_progression({
            "id": "test_prog_1",
            "name": "Test Progression 1",
            "chords": ["C", "Am", "F", "G"],
            "key": "C",
            "scale_type": "major",
            "complexity": 0.5
        }),
        format_chord_progression({
            "id": "test_prog_2",
            "name": "Test Progression 2",
            "chords": ["Dm", "G", "Em", "Am"],
            "key": "D",
            "scale_type": "minor",
            "complexity": 0.7
        })
    ]
    
    note_patterns = [
        format_note_pattern({
            "id": "test_pattern_1",
            "name": "Test Pattern 1",
            "notes": [{"note_name": "C", "octave": 4, "duration": 1.0}],
            "pattern_type": "melodic",
            "complexity": 0.5
        }),
        format_note_pattern({
            "id": "test_pattern_2",
            "name": "Test Pattern 2",
            "notes": [{"note_name": "E", "octave": 4, "duration": 0.5}],
            "pattern_type": "harmonic",
            "complexity": 0.6
        })
    ]
    
    rhythm_patterns = [
        format_rhythm_pattern({
            "id": "test_rhythm_1",
            "name": "Test Rhythm 1",
            "beats": [1, 0, 1, 0],
            "complexity": 0.4
        }),
        format_rhythm_pattern({
            "id": "test_rhythm_2",
            "name": "Test Rhythm 2",
            "beats": [1, 1, 0, 1],
            "complexity": 0.6
        })
    ]
    
    # Clear existing data
    await test_db.chord_progressions.delete_many({})
    await test_db.note_patterns.delete_many({})
    await test_db.rhythm_patterns.delete_many({})
    
    # Insert sample data
    await test_db.chord_progressions.insert_many(chord_progressions)
    await test_db.note_patterns.insert_many(note_patterns)
    await test_db.rhythm_patterns.insert_many(rhythm_patterns)
    
    yield
    
    # Cleanup after tests
    await test_db.chord_progressions.delete_many({})
    await test_db.note_patterns.delete_many({})
    await test_db.rhythm_patterns.delete_many({})

# Register cleanup function
def cleanup() -> None:
    """Clean up resources when the tests are done."""
    client.close()
    mock_client.close()

atexit.register(cleanup)