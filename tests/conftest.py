"""Test configuration and fixtures."""

import os
import sys
import asyncio
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import necessary modules
from .test_fetch_patterns import (
    SAMPLE_CHORD_PROGRESSIONS,
    SAMPLE_NOTE_PATTERNS,
    SAMPLE_RHYTHM_PATTERNS,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.tests.conftest")

# MongoDB settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("TEST_DATABASE_NAME", "test_note_gen")

# MongoDB client instance
client = None

# Set testing environment variable
os.environ["TESTING"] = "1"

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def mongo_client(event_loop):
    """Create a MongoDB client."""
    global client
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        logger.info("MongoDB client connected.")
        logger.info(f"Connected to MongoDB at {MONGODB_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.error(f"Error connecting to MongoDB at {MONGODB_URL}: {e}")

    try:
        yield client
    finally:
        if client:
            client.close()
            logger.info("MongoDB client connection closed.")
            logger.info(f"Disconnected from MongoDB at {MONGODB_URL}")

@pytest.fixture(autouse=True)
async def setup_test_db(mongo_client, event_loop):
    global db
    db = mongo_client["test_note_gen"]
    
    # Clear test database
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    
    yield db
    
    # Cleanup
    mongo_client.drop_database('test_note_gen')

@pytest_asyncio.fixture(scope="function")
async def clean_test_db(setup_test_db):
    db = setup_test_db
    try:
        # Insert sample data for chord progressions
        if SAMPLE_CHORD_PROGRESSIONS:
            documents = [
                {
                    "_id": prog["id"],
                    "id": prog["id"],
                    "name": prog["name"],
                    "complexity": prog["complexity"],
                    "key": prog["key"],
                    "scale_type": prog["scale_type"].value if hasattr(prog["scale_type"], "value") else prog["scale_type"],
                    "chords": [
                        {
                            "root": {
                                "note_name": chord["root"].note_name,
                                "octave": chord["root"].octave,
                                "duration": int(chord["root"].duration),  
                                "velocity": 100
                            },
                            "quality": chord["quality"].value if hasattr(chord["quality"], "value") else chord["quality"],
                            "notes": [
                                {
                                    "note_name": note.note_name,
                                    "octave": note.octave,
                                    "duration": int(note.duration),  
                                    "velocity": 100
                                }
                                for note in chord["notes"]
                            ],
                        } for chord in prog["chords"]
                    ],
                } for prog in SAMPLE_CHORD_PROGRESSIONS
            ]
            result = await db.chord_progressions.insert_many(documents)
            logger.info("Sample chord progressions inserted.")

        # Insert sample data for note patterns
        if SAMPLE_NOTE_PATTERNS:
            await db.note_patterns.insert_many([
                {
                    "_id": pattern["id"],
                    "id": pattern["id"],
                    "name": pattern["name"],
                    "data": pattern["data"],
                    "notes": [
                        note.dict() if hasattr(note, "dict") else note for note in pattern["notes"]
                    ],
                    "description": pattern["description"],
                    "tags": pattern["tags"],
                    "is_test": pattern["is_test"],
                } for pattern in SAMPLE_NOTE_PATTERNS
            ])
            logger.info("Sample note patterns inserted.")

        # Insert sample data for rhythm patterns
        if SAMPLE_RHYTHM_PATTERNS:
            await db.rhythm_patterns.insert_many([
                {
                    "_id": pattern["id"],
                    "id": pattern["id"],
                    "name": pattern["name"],
                    "data": pattern["data"].dict() if hasattr(pattern["data"], "dict") else pattern["data"],
                    "description": pattern["description"],
                    "complexity": pattern["complexity"],
                    "style": pattern["style"],
                    "pattern": pattern["pattern"],
                    "is_test": pattern["is_test"],
                } for pattern in SAMPLE_RHYTHM_PATTERNS
            ])
            logger.info("Sample rhythm patterns inserted.")
    except Exception as e:
        logger.error(f"Error while inserting sample data: {e}")
        raise

    return db

class MockDatabase:
    def __init__(self):
        self.data = {
            "note_patterns": [],
            "chord_progressions": [],
            "rhythm_patterns": [],
        }

    def note_patterns(self):
        return self.data["note_patterns"]

    def chord_progressions(self):
        return self.data["chord_progressions"]

    def rhythm_patterns(self):
        return self.data["rhythm_patterns"]

    def insert_many(self, collection_name, documents):
        logger.info(f"Inserting {len(documents)} documents into {collection_name}.")
        if collection_name in self.data:
            self.data[collection_name].extend(documents)
        else:
            raise ValueError(f"Collection '{collection_name}' does not exist in the mock database.")

@pytest_asyncio.fixture(scope="function")
async def mock_db(clean_test_db):
    """Provide a mock database for testing."""
    mock_db = MockDatabase()
    mock_data = {
        "note_patterns": [
            {
                "_id": "mock_note_pattern_id",
                "id": "mock_note_pattern_id",
                "name": "Mock Note Pattern",
                "data": "Mock data",
                "notes": [
                    {
                        "note_name": "C",
                        "octave": 4,
                        "duration": 1,
                        "velocity": 100
                    }
                ],
                "description": "Mock description",
                "tags": ["mock_tag"],
                "is_test": True,
            }
        ],
        "rhythm_patterns": [
            {
                "_id": "mock_rhythm_pattern_id",
                "id": "mock_rhythm_pattern_id",
                "name": "Mock Rhythm Pattern",
                "data": "Mock data",
                "description": "Mock description",
                "complexity": 1,
                "style": "Mock style",
                "pattern": "Mock pattern",
                "is_test": True,
            }
        ],
        "chord_progressions": [
            {
                "_id": "mock_chord_progression_id",
                "id": "mock_chord_progression_id",
                "name": "Mock Chord Progression",
                "complexity": 1,
                "key": "C",
                "scale_type": "Major",
                "chords": [
                    {
                        "root": {
                            "note_name": "C",
                            "octave": 4,
                            "duration": 1,
                            "velocity": 100
                        },
                        "quality": "Major",
                        "notes": [
                            {
                                "note_name": "C",
                                "octave": 4,
                                "duration": 1,
                                "velocity": 100
                            }
                        ],
                    }
                ],
            }
        ]
    }

    for collection_name, documents in mock_data.items():
        mock_db.insert_many(collection_name, documents)
    return mock_db

def pytest_sessionfinish(session, exitstatus):
    """Clean up after all tests are done."""
    global client
    if client:
        client.close()
        logger.info("MongoDB client connection closed.")
        logger.info(f"Disconnected from MongoDB at {MONGODB_URL}")

# Ensure custom test utilities are registered for assertions
pytest.register_assert_rewrite("tests.utils")