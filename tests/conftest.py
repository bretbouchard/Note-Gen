"""Test configuration and fixtures."""

import os
import sys


# Set testing environment variable
os.environ["TESTING"] = "1"
# Set the MongoDB test URI to connect to the test_note_gen database
os.environ["MONGODB_TEST_URI"] = "mongodb://localhost:27017/test_note_gen"

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)


import pytest
import asyncio
import motor.motor_asyncio
import logging
import httpx
from fastapi.testclient import TestClient
from src.note_gen.main import app  # Update the import path
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")

class MockDatabase:
    """Mock database for testing."""
    def __init__(self):
        self.chord_progressions = {}
        self.note_patterns = {}
        self.rhythm_patterns = {}
        self.presets = {}

    async def find_one(self, collection, query):
        """Mock find_one operation."""
        return self.get_collection(collection).get(query.get("_id"))

    async def insert_one(self, collection, document):
        """Mock insert_one operation."""
        self.get_collection(collection)[document["_id"]] = document

    async def delete_one(self, collection, query):
        """Mock delete_one operation."""
        collection_data = self.get_collection(collection)
        if query.get("_id") in collection_data:
            del collection_data[query["_id"]]

    def get_collection(self, collection_name):
        """Get the appropriate collection dictionary."""
        collections = {
            "chord_progressions": self.chord_progressions,
            "note_patterns": self.note_patterns,
            "rhythm_patterns": self.rhythm_patterns,
            "presets": self.presets
        }
        return collections.get(collection_name, {})

@pytest.fixture
def mock_db():
    """Fixture to provide a mock database."""
    return MockDatabase()


@pytest.fixture
def test_app():
    return TestClient(app)

@pytest.fixture
async def async_client():
    app.dependency_overrides = {}  # Reset any overrides
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


async def clean_test_db():
    client = AsyncIOMotorClient('localhost', 27017)
    if client is None:
        logger.error("Error: MongoDB client is not initialized.")
    else:
        logger.info("MongoDB client initialized successfully.")
    db = client.test_note_gen
    await db.chord_progressions.delete_many({})
    await db.rhythm_patterns.delete_many({})
    await db.note_patterns.delete_many({})
    
    # Add sample data
    await db.chord_progressions.insert_many([
        {
            "name": "Sample Progression",
            "chords": [
                {"name": "C", "root": {"note": "C", "octave": 4}, "quality": "major", "intervals": [0, 4, 7]}
            ],
            "key": "C",
            "scale_type": "major"
        }
    ])
    
    yield db
    if client is not None:
        logger.info("Closing MongoDB client.")
        await client.close()


@pytest.fixture
async def mongo_client(event_loop):
    """Create a MongoDB client for testing."""
    client = motor.motor_asyncio.AsyncIOMotorClient(
        MONGODB_URL,
        io_loop=event_loop
    )
    yield client
    client.close()