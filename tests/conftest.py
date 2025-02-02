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
        self._collections = {
            'chord_progressions': {},
            'note_patterns': {},
            'rhythm_patterns': {},
            'presets': {}
        }
        self.name = "test_db"  # Add name attribute for testing
        
        class Collection:
            def __init__(self, data):
                self.data = data

            def find(self, query=None):
                if query is None:
                    query = {}
                results = []
                for doc in self.data.values():
                    if all(doc.get(k) == v for k, v in query.items()):
                        results.append(doc)

                class Cursor:
                    def __init__(self, results):
                        self.results = results

                    async def to_list(self, length=None):
                        return self.results[:length] if length else self.results

                    async def __aiter__(self):
                        for result in self.results:
                            yield result

                return Cursor(results)

            async def find_one(self, query=None):
                if query is None:
                    query = {}
                if '_id' in query:
                    return self.data.get(query['_id'])
                if 'id' in query:
                    for doc in self.data.values():
                        if doc.get('id') == query['id']:
                            return doc
                for doc in self.data.values():
                    if all(doc.get(k) == v for k, v in query.items()):
                        return doc
                return None

            async def insert_one(self, document):
                if '_id' not in document:
                    document['_id'] = str(len(self.data) + 1)
                self.data[document['_id']] = document
                return type('InsertOneResult', (), {'inserted_id': document['_id']})

            async def delete_one(self, query):
                if '_id' in query:
                    return self.data.pop(query['_id'], None)
                return None

            async def update_one(self, query, update, upsert=False):
                if '_id' in query:
                    doc = self.data.get(query['_id'])
                    if doc:
                        doc.update(update.get('$set', {}))
                        return type('UpdateResult', (), {'modified_count': 1})
                return type('UpdateResult', (), {'modified_count': 0})

            async def insert_many(self, documents):
                inserted_ids = []
                for document in documents:
                    if '_id' not in document and 'id' in document:
                        document['_id'] = document['id']
                    if '_id' not in document:
                        document['_id'] = str(len(self.data) + 1)
                    self.data[document['_id']] = document
                    inserted_ids.append(document['_id'])
                return type('InsertManyResult', (), {'inserted_ids': inserted_ids})

            @staticmethod
            async def __aiter__(results):
                for result in results:
                    yield result

        # Create collection properties
        for collection_name, data in self._collections.items():
            setattr(self, collection_name, Collection(data))

    async def insert_many(self, collection_name, documents):
        """Mock insert_many operation."""
        collection = getattr(self, collection_name)
        return await collection.insert_many(documents)

    def insert_data(self, collection_name, data):
        """Insert data into the mock database."""
        collection = getattr(self, collection_name)
        for document in data:
            if '_id' not in document:
                document['_id'] = document.get('id', str(len(collection.data) + 1))
            collection.data[document['_id']] = document

@pytest.fixture
def mock_db():
    return MockDatabase()

@pytest.fixture
def mock_db_with_data():
    db = MockDatabase()
    db.insert_data('note_patterns', [
        {"_id": "note_pattern_1", "name": "Pattern 1", "description": "This is pattern 1"},
        {"_id": "note_pattern_2", "name": "Pattern 2", "description": "This is pattern 2"},
    ])
    db.insert_data('rhythm_patterns', [
        {"_id": "rhythm_pattern_1", "name": "Pattern 1", "description": "This is pattern 1"},
        {"_id": "rhythm_pattern_2", "name": "Pattern 2", "description": "This is pattern 2"},
    ])
    db.insert_data('chord_progressions', [
        {"_id": "chord_progression_1", "name": "Progression 1", "description": "This is progression 1"},
        {"_id": "chord_progression_2", "name": "Progression 2", "description": "This is progression 2"},
    ])
    return db

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