import os
import sys
import pytest
import mongomock
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
import uvicorn
import threading
import logging
from typing import Any, Generator
from fastapi.testclient import TestClient

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.note_gen.routers.user_routes import app, get_db

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_test_db() -> Generator[Database[Any], None, None]:
    """Get test database connection."""
    client = mongomock.MongoClient()
    db = client.db
    yield db
    client.close()

@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """Provides a FastAPI test client for testing."""
    app.dependency_overrides[get_db] = get_test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}

@pytest.fixture(scope="session")
def mock_db() -> Database[Any]:
    """Creates a mock MongoDB client."""
    client = mongomock.MongoClient()
    db = client.db
    yield db
    client.close()

@pytest.fixture(autouse=True)
def setup_test_db(mock_db: Database[Any]) -> Generator[None, None, None]:
    """Sets up the mock database for tests."""
    original_client = pymongo.MongoClient
    pymongo.MongoClient = mongomock.MongoClient  # Use mongomock directly
    logger.debug("Mock MongoDB client set up.")
    
    yield
    
    pymongo.MongoClient = original_client  # Restore the original client
    logger.debug("Mock MongoDB client restored.")

@pytest.fixture(scope="session", autouse=True)
def start_server() -> Generator[None, None, None]:
    """Starts the FastAPI server in a separate thread."""
    server = threading.Thread(target=uvicorn.run, args=(app,), kwargs={'host': 'localhost', 'port': 8000})
    server.start()
    logger.debug("FastAPI server started.")
    
    yield
    
    app.dependency_overrides = {}  # Clear dependency overrides
    server.join()
    logger.debug("FastAPI server stopped.")