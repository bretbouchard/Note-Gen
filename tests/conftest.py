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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.note_gen.routers.user_routes import router, get_db

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_test_db() -> Generator[Database[Any], None, None]:
    """Get test database connection."""
    client = mongomock.MongoClient()
    db = client.db
    yield db
    client.close()

def create_test_app() -> FastAPI:
    """Create a FastAPI app for testing."""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.dependency_overrides[get_db] = get_test_db
    return app

@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """Provides a FastAPI app for testing."""
    return create_test_app()

@pytest.fixture(scope="session")
def test_client(test_app: FastAPI) -> TestClient:
    """Provides a FastAPI test client for testing."""
    with TestClient(test_app) as client:
        yield client

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