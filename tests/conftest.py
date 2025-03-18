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
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
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
from src.note_gen import app
from src.note_gen.database.db import init_db, close_mongo_connection, get_db_conn, drop_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.fetch_patterns import extract_patterns_from_chord_progressions

# Import proper models for test data
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.patterns import NotePattern, NotePatternData, RhythmPattern, RhythmPatternData

@pytest.fixture(scope="session")
def event_loop_policy():
    """Create and set a new event loop policy for the test session."""
    policy = asyncio.get_event_loop_policy()
    return policy

@pytest.fixture
async def event_loop(event_loop_policy):
    """Create and yield a new event loop for each test."""
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

# -------------------------------
# Fixtures
# -------------------------------

@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Create a test database connection."""
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client['test_note_gen']
    yield db
    await client.drop_database('test_note_gen')
    client.close()

@pytest.fixture(scope="session")
def sync_client():
    return TestClient(app)

@pytest_asyncio.fixture(scope="session")
async def async_client(test_db):
    async with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session")
async def global_cleanup(test_db):
    yield
    await test_db.client.drop_database("test_note_gen")

@pytest.fixture(scope="session")
def mongodb():
    # Use test database configuration
    MONGODB_TEST_URL = os.getenv("MONGODB_TEST_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(MONGODB_TEST_URL, serverSelectionTimeoutMS=5000)
    return client
