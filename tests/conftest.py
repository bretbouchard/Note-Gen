import asyncio
import logging
import os
import sys
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional, Tuple

import motor.motor_asyncio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, field_validator
from pytest_asyncio import fixture

from src.note_gen.dependencies import get_db

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a test-specific FastAPI instance
app = FastAPI()

# Import your route handlers
from src.note_gen.routers.user_routes import router as user_router
from src.note_gen.routers.chord_progression_routes import router as chord_progression_router
from src.note_gen.routers.note_sequence_routes import router as note_sequence_router
from src.note_gen.routers.rhythm_pattern_routes import router as rhythm_patterns_router
from src.note_gen.routers.note_pattern_routes import router as note_pattern_router

# Include the routers
app.include_router(user_router, prefix="/api/v1/users")
app.include_router(chord_progression_router, prefix="/api/v1/chord-progressions")
app.include_router(note_sequence_router, prefix="/api/v1/note-sequences")
app.include_router(rhythm_patterns_router, prefix="/api/v1/rhythm-patterns")
app.include_router(note_pattern_router, prefix="/api/v1/note-patterns")

# Set testing environment variable
os.environ["TESTING"] = "1"
os.environ["MONGODB_TEST_URI"] = "mongodb://localhost:27017/test_note_gen"

# Configure logging
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")

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
        arbitrary_types_allowed = True

    @field_validator('notes')
    def validate_notes(cls, value):
        if not value:
            raise ValueError('Notes must not be empty')
        return value

class RhythmPattern(BaseModel):
    id: Optional[str]
    name: str
    data: RhythmPatternData
    description: str
    tags: List[str]
    complexity: Optional[float]
    style: Optional[str]

    class Config:
        arbitrary_types_allowed = True

    @field_validator('name')
    def validate_name(cls, value):
        if not value:
            raise ValueError('Name must not be empty')
        return value

class MockDatabase:
    """Mock database for testing."""

    def __init__(self, uri: str) -> None:
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_TEST_URI"])
            logger.debug("MongoDB client initialized successfully.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise RuntimeError("Failed to initialize MongoDB client.") from e
        self.name = "test_db"  # Add name attribute for testing
        
        # Initialize collections with empty dictionaries
        self._collections = {
            'note_patterns': {},
            'rhythm_patterns': {},
            'chord_progressions': {}
        }
        
    async def find(self, query: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        results: List[Dict[str, Any]] = []
        if query is None:
            query = {}
        for doc in self._collections.values():
            if all(doc.get(k) == v for k, v in query.items()):
                results.append(doc)
        for result in results:
            yield result

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> None:
        collection = getattr(self, collection_name)
        for document in data:
            if '_id' not in document:
                document['_id'] = str(len(collection) + 1)
            collection[document['_id']] = document

    async def create_index(self, collection_name: str, keys: List[Tuple[str, int]], unique: bool = False) -> None:
        pass

    class Collection:
        def __init__(self, data: Dict[str, Any]) -> None:
            self.data = data

        async def find(self, query: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
            results: List[Dict[str, Any]] = []
            if query is None:
                query = {}
            for doc in self.data.values():
                if all(doc.get(k) == v for k, v in query.items()):
                    results.append(doc)
            for result in results:
                yield result

        async def find_one(self, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
            if query is None:
                query = {}
            if '_id' in query:
                return self.data.get(query['_id'], None)  # Ensure it returns None if not found
            return None

        async def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
            if '_id' not in document:
                document['_id'] = str(len(self.data) + 1)
            self.data[document['_id']] = document
            return {'inserted_id': document['_id']}

        async def delete_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            if '_id' in query:
                return self.data.pop(query['_id'], None)
            return None

        async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> Dict[str, Any]:
            if '_id' in query:
                doc = self.data.get(query['_id'])
                if doc:
                    doc.update(update.get('$set', {}))
                    return {'modified_count': 1}
            return {'modified_count': 0}

        async def insert_many(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
            inserted_ids = []
            for document in documents:
                if '_id' not in document:
                    document['_id'] = str(len(self.data) + 1)
                self.data[document['_id']] = document
                inserted_ids.append(document['_id'])
            return {'inserted_ids': inserted_ids}

        async def __aiter__(self) -> AsyncGenerator[Dict[str, Any], None]:
            for result in self.data.values():
                yield result

    async def setup_collections(self) -> None:
        """
        Setup collections for the mock database.
        This method ensures that all required collections are initialized.
        """
        # Create collection instances for each collection type
        self.note_patterns = self.Collection(self._collections['note_patterns'])
        self.rhythm_patterns = self.Collection(self._collections['rhythm_patterns'])
        self.chord_progressions = self.Collection(self._collections['chord_progressions'])

    @property
    def client(self):
        """Simulate the client property for compatibility."""
        return self

    @property
    def test_db(self):
        """Simulate the test_db property for compatibility."""
        return self

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the event loop for the entire test session.
    This ensures that the event loop is properly managed across tests.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    policy.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def client(event_loop):
    """
    Create an async test client for the FastAPI application.
    Uses the session-scoped event loop.
    """
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        yield client

@pytest.fixture
async def mock_db_with_data() -> MockDatabase:
    # Sample note patterns to insert into the mock database
    sample_note_patterns = [
        {
            "_id": "note_pattern_1",
            "id": "note_pattern_1",
            "name": "Basic triad arpeggio",
            "description": "A simple triad arpeggio pattern",
            "tags": ["basic", "arpeggio"],
            "intervals": [0, 4, 7],
            "duration": 1.0,
            "position": 0.0,
            "velocity": 100,
            "data": {
                "notes": [],
                "intervals": [0, 4, 7],
                "duration": 1.0,
                "position": 0.0,
                "velocity": 100,
                "index": 0
            }
        }
    ]

    # Sample rhythm patterns to insert into the mock database
    sample_rhythm_patterns = [
        {
            "_id": "rhythm_pattern_1",
            "id": "rhythm_pattern_1",
            "name": "Basic Rock Beat",
            "description": "A simple rock rhythm pattern",
            "tags": ["rock", "basic"],
            "data": {
                "notes": [
                    {"position": 0.0, "duration": 0.5, "velocity": 100, "is_rest": False},
                    {"position": 0.5, "duration": 0.5, "velocity": 80, "is_rest": False}
                ],
                "time_signature": "4/4",
                "total_duration": 1.0
            },
            "complexity": 0.5,
            "style": "Rock"
        }
    ]

    # Sample chord progressions to insert into the mock database
    sample_chord_progressions = [
        {
            "_id": "progression_1",
            "id": "progression_1",
            "name": "I-IV-V",
            "chords": [
                {"root": "C", "quality": "MAJOR"},
                {"root": "F", "quality": "MAJOR"},
                {"root": "G", "quality": "MAJOR"}
            ],
            "key": "C",
            "scale_type": "MAJOR",
            "complexity": 0.5
        }
    ]

    # Create a new MockDatabase
    mock_db = MockDatabase(os.environ["MONGODB_TEST_URI"])
    
    # Initialize the collections
    await mock_db.setup_collections()
    
    # Insert sample data into collections
    mock_db.note_patterns.data = {p['_id']: p for p in sample_note_patterns}
    mock_db.rhythm_patterns.data = {p['_id']: p for p in sample_rhythm_patterns}
    mock_db.chord_progressions.data = {p['_id']: p for p in sample_chord_progressions}
    
    return mock_db

@pytest.fixture(scope="session")
def test_client():
    logger.info("Initializing TestClient...")
    client = TestClient(app)
    yield client
    logger.info("TestClient teardown...")

@pytest.fixture(scope="session")
def mongo_client():
    logger.info("Initializing MongoDB client...")
    client = motor.motor_asyncio.AsyncIOMotorClient()
    try:
        yield client
    except Exception as e:
        logger.error(f"MongoDB client initialization failed: {e}")
        raise
    finally:
        client.close()
        logger.info("MongoDB client closed.")

@pytest.fixture(scope="function")
async def clean_test_db() -> AsyncGenerator[None, None]:
    try:
        db = AsyncIOMotorClient(os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017"))[os.getenv("DATABASE_NAME", "note_gen_test")]
        collections = await db.list_collection_names()
        for collection in collections:
            # Drop all indexes first
            await db[collection].drop_indexes()
            # Then drop the collection
            await db.drop_collection(collection)
        logger.info("Test database cleaned successfully")
    except Exception as e:
        logger.error(f"Error cleaning test database: {str(e)}")
        raise

@pytest.fixture
def client():
    logger.debug("Creating FastAPI TestClient for app instance.")
    with TestClient(app) as client:
        logger.debug("FastAPI TestClient created successfully for app instance.")
        yield client

@pytest.fixture(scope="function")
async def setup_test_db(clean_test_db: None) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Setup test database with proper event loop handling."""
    try:
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_TEST_URI"])
            logger.debug("MongoDB client initialized successfully.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise RuntimeError("Failed to initialize MongoDB client.") from e
        db = client[os.getenv("DATABASE_NAME", "note_gen_test")]
        
        # Ensure database is clean
        await clean_test_db
        
        # Setup indexes
        await ensure_indexes(db)
        
        # Import test data
        await import_presets_if_empty(db)
        
        yield db
        
        # Cleanup after test
        await clean_test_db
        
    except Exception as e:
        logger.error(f"Error in setup_test_db: {str(e)}")
        raise
    finally:
        client.close()

@pytest.fixture
async def init_test_data(mongo_client: AsyncIOMotorClient):
    """Initialize test data."""
    db = mongo_client.get_database()
    
    # Test data
    chord_progression = {
        "name": "Test Progression",
        "chords": [
            {
                "root": {"note_name": "C", "octave": 4},
                "quality": "MAJOR",
                "notes": [],
                "inversion": 0
            }
        ],
        "key": "C",
        "scale_type": "MAJOR"
    }
    
    note_pattern = {
        "name": "Test Pattern",
        "notes": [
            {
                "note_name": "C",
                "octave": 4,
                "duration": 1.0,
                "velocity": 100
            }
        ],
        "description": "Test pattern",
        "tags": ["test"]
    }
    
    rhythm_pattern = {
        "name": "Test Rhythm",  # Updated to previous test name
        "id": "test_1",
        "description": "A simple on-off rhythm pattern.",
        "tags": ["basic", "rhythm"],
        "data": {
            "notes": [
                {"position": 0, "duration": 1.0, "velocity": 100, "is_rest": False},
                {"position": 1, "duration": 1.0, "velocity": 100, "is_rest": True},
                {"position": 2, "duration": 1.0, "velocity": 100, "is_rest": False},
                {"position": 3, "duration": 1.0, "velocity": 100, "is_rest": True}
            ],
            "time_signature": "4/4",
            "pattern": [1, -1, 1, -1]
        }
    }
    
    # Insert test data
    await db.chord_progressions.insert_one(chord_progression)
    await db.note_patterns.insert_one(note_pattern)
    await db.rhythm_patterns.insert_one(rhythm_pattern)