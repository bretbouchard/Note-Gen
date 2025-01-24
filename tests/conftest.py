import os
import sys
import pytest
import asyncio
import motor.motor_asyncio
import logging
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a test-specific FastAPI instance
app = FastAPI()

# Import your route handlers
from src.note_gen.routers.user_routes import router as user_router
from src.note_gen.routers.chord_progression_routes import router as chord_progression_router

# Include the routers
app.include_router(user_router)
app.include_router(chord_progression_router)

# Set testing environment variable
os.environ["TESTING"] = "1"
os.environ["MONGODB_TEST_URI"] = "mongodb://localhost:27017/test_note_gen"

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
    return MockDatabase()

@pytest.fixture
def test_app():
    return app

@pytest.fixture
async def async_client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def clean_test_db(event_loop):
    """Clean and initialize test database."""
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client.test_note_gen
    
    # Clear all collections
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    
    yield db
    
    # Cleanup after tests
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})
    client.close()

@pytest.fixture
async def mongo_client(event_loop):
    """Create a MongoDB client for testing."""
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    yield client
    client.close()