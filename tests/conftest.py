"""
Test fixtures and configuration.
"""

import os
import sys
import asyncio
import logging
import pytest
import pytest_asyncio
import httpx
import threading
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional, Tuple, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.note_gen.database.db import init_db, close_mongo_connection, get_db_conn
from src.note_gen.main import app
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from pydantic import BaseModel, ConfigDict, field_validator
from fastapi import FastAPI
from httpx import ASGITransport
from contextlib import asynccontextmanager

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set testing environment variable
os.environ['TESTING'] = '1'
os.environ['MONGODB_TEST_URI'] = 'mongodb://localhost:27017/test_note_gen'
os.environ['DATABASE_NAME'] = 'test_note_gen'

# Configure logging
class ThreadSafeStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()

    def emit(self, record):
        with self._lock:
            try:
                if not self.stream.closed:
                    super().emit(record)
            except Exception:
                self.handleError(record)

# Configure root logger
handler = ThreadSafeStreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)

# Configure specific loggers
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017/test_note_gen")

class Note(BaseModel):
    note_name: str
    octave: int
    duration: float
    velocity: int

class NotePatternData(BaseModel):
    notes: List[Dict[str, Any]]
    duration: float
    position: float
    velocity: int
    intervals: List[Any]
    index: int

    class Config:
        config = ConfigDict(arbitrary_types_allowed=True)

class NotePattern(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    notes: List[Note]
    data: NotePatternData
    intervals: List[Any]
    duration: float
    position: float
    velocity: float

class Chord(BaseModel):
    pass  # Define the Chord model

class ChordProgression(BaseModel):
    index: int
    id: str
    name: str
    chords: List[Chord]
    key: str
    scale_type: str
    complexity: float

class RhythmNote(BaseModel):
    position: float
    duration: float
    velocity: int
    is_rest: bool

class RhythmPatternData(BaseModel):
    notes: List[RhythmNote]
    time_signature: str
    swing_ratio: Optional[float]
    default_duration: Optional[float]
    total_duration: Optional[float]
    groove_type: Optional[str]

    class Config:
        config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('notes')
    def validate_notes(cls, value):
        if not value:
            raise ValueError('Notes must not be empty')
        return value

@pytest.fixture
async def test_db():
    """Fixture to provide a test database."""
    await init_db()
    db = await get_db_conn()
    
    # Clear all collections before each test
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].delete_many({})
    
    # Sample data to insert
    test_chord_progressions = [
        {"name": "I-IV-V-I", "chords": ["C", "F", "G", "C"]},
        {"name": "ii-V-I", "chords": ["Dm", "G", "C"]}
    ]
    test_note_patterns = [
        {"name": "Simple Triad", "notes": ["C", "E", "G"]},
        {"name": "Major Scale", "notes": ["C", "D", "E", "F", "G", "A", "B"]}
    ]
    test_rhythm_patterns = [
        {"name": "quarter_notes", "pattern": [1, 0, 1, 0]},
        {"name": "eighth_notes", "pattern": [1, 1, 0, 0]}
    ]

    # Insert sample data into the database
    await db.chord_progressions.insert_many(test_chord_progressions)
    await db.note_patterns.insert_many(test_note_patterns)
    await db.rhythm_patterns.insert_many(test_rhythm_patterns)
    
    yield db
    
    # Clean up after test
    await close_mongo_connection()

@pytest.fixture
async def async_test_client():
    """Fixture to provide an async test client."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        yield client