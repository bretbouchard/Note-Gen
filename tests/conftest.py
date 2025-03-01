import os
import sys
import asyncio
import logging
import threading
import pytest
import pytest_asyncio
import httpx
from fastapi.testclient import TestClient
from httpx import ASGITransport
from typing import Any, AsyncGenerator, Generator, List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)
logger.propagate = True

# Load environment variables from .env file
load_dotenv()
logger.debug(f'Environment variables after loading .env file: {os.environ}')
logger.debug(f'Value of CLEAR_DB_AFTER_TESTS before tests: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
logger.debug(f'CLEAR_DB_AFTER_TESTS value after loading .env: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
logger.debug(f'CLEAR_DB_AFTER_TESTS value after loading .env: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
logger.debug(f'Value of CLEAR_DB_AFTER_TESTS before tests: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
# Explicitly set CLEAR_DB_AFTER_TESTS to '0'
os.environ['CLEAR_DB_AFTER_TESTS'] = '0'

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set testing environment variables
os.environ['TESTING'] = '1'
os.environ['MONGODB_TEST_URI'] = 'mongodb://localhost:27017/test_note_gen'
os.environ['DATABASE_NAME'] = 'test_note_gen'

# Define a thread-safe logging handler.
# Note: We add a type parameter "[Any]" to satisfy MyPy.
class ThreadSafeStreamHandler(logging.StreamHandler[Any]):
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        with self._lock:
            try:
                if not self.stream.closed:
                    super().emit(record)
            except Exception:
                self.handleError(record)

handler: ThreadSafeStreamHandler = ThreadSafeStreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.root.addHandler(handler)

logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Import the FastAPI app and database functions.
from main import app
from src.note_gen.database.db import init_db, close_mongo_connection, get_db_conn
from motor.motor_asyncio import AsyncIOMotorDatabase

# Minimal model definitions for sample data insertion.
from pydantic import BaseModel, validator, field_validator

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
        arbitrary_types_allowed = True

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
    pass  # Replace with your actual Chord model

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
    swing_ratio: Any  # Use a more specific type if available
    default_duration: Any
    total_duration: Any
    groove_type: Any

    class Config:
        arbitrary_types_allowed = True

    @field_validator('notes')
    def validate_notes(cls, value: List[RhythmNote]) -> List[RhythmNote]:
        if not value:
            raise ValueError('Notes must not be empty')
        return value

# -------------------------------
# Fixtures
# -------------------------------

@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    """
    Provides a test database connection with sample data.
    """
    logger.debug('Entering test_db fixture')
    db: AsyncIOMotorDatabase[Any] = await get_db_conn()
    clear_db_after_tests = os.getenv('CLEAR_DB_AFTER_TESTS', '1')
    logger.debug(f'CLEAR_DB_AFTER_TESTS value: {clear_db_after_tests}')
    logger.debug(f'CLEAR_DB_AFTER_TESTS value: {os.getenv("CLEAR_DB_AFTER_TESTS")}')
    if os.getenv('CLEAR_DB_AFTER_TESTS', '1') == '1':
        logger.debug('Clearing database collections')
        collections: List[str] = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})
    logger.debug('Inserting sample data into database')
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
    await db.chord_progressions.insert_many(test_chord_progressions)
    await db.note_patterns.insert_many(test_note_patterns)
    await db.rhythm_patterns.insert_many(test_rhythm_patterns)
    logger.debug('Yielding database connection')
    yield db
    logger.debug('Closing database connection')
    await close_mongo_connection()

@pytest_asyncio.fixture
async def async_test_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Provides an async test client.
    """
    logger.debug('Entering async_test_client fixture')
    transport: ASGITransport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        logger.debug('Yielding async test client')
        yield client

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """
    Provides a synchronous test client.
    """
    with TestClient(app=app) as client:
        yield client