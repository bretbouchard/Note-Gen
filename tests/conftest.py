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
async def mongo_client():
    """Create a MongoDB client."""
    global client
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        logger.info("MongoDB client connected.")
        yield client
    finally:
        if client:
            client.close()
            logger.info("MongoDB client connection closed.")

@pytest_asyncio.fixture(scope="function")
async def clean_test_db(mongo_client: AsyncIOMotorClient) -> None:
    db = mongo_client.test_note_gen
    try:
        await db.drop_collection("chord_progressions")
        await db.drop_collection("note_patterns")
        await db.drop_collection("rhythm_patterns")
        logger.info("Test database cleared.")

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

@pytest_asyncio.fixture(scope="function")
async def mock_db(clean_test_db):
    """Provide a mock database for testing."""
    # Create a mock implementation of the database
    class MockCursor:
        def __init__(self, data):
            self.data = data
            self.index = 0
    
        async def __anext__(self):
            if self.index < len(self.data):
                result = self.data[self.index]
                self.index += 1
                await asyncio.sleep(0)  # Simulate async behavior
                return result
            else:
                raise StopAsyncIteration
    
        def __aiter__(self):
            return self

    # Mock the database collections with sample data
    mock_data = {
        "note_patterns": [
            {"_id": "1", "name": "Pattern 1", "notes": []},
            {"_id": "2", "name": "Pattern 2", "notes": []},
        ],
        "rhythm_patterns": [
            {"_id": "1", "name": "Rhythm 1", "data": {}}
        ],
        "chord_progressions": [
            {"_id": "1", "name": "Progression 1", "chords": []}
        ],
    }

    # Mock the database methods
    class MockDatabase:
        def __init__(self, data):
            self.data = data

        async def note_patterns(self):
            return MockCursor(self.data["note_patterns"])

        async def rhythm_patterns(self):
            return MockCursor(self.data["rhythm_patterns"])

        async def chord_progressions(self):
            return MockCursor(self.data["chord_progressions"])

        async def find_one(self, query):
            for doc in self.data["note_patterns"]:
                if doc.get("_id") == query.get("_id"):
                    return doc
            return None

        async def insert_one(self, doc):
            self.data["note_patterns"].append(doc)
            return doc

    # Return the mock database instance
    return MockDatabase(mock_data)

def pytest_sessionfinish(session, exitstatus):
    """Clean up after all tests are done."""
    global client
    if client:
        client.close()

# Ensure custom test utilities are registered for assertions
pytest.register_assert_rewrite("tests.utils")