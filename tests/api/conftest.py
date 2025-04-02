"""API test fixtures."""
import pytest
from typing import AsyncIterator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from httpx import AsyncClient, ASGITransport
from src.note_gen.main import app
from src.note_gen.database.db import get_db_conn
from src.note_gen.app import app, limiter
from src.note_gen.config import settings

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset the rate limiter before each test."""
    # Clear the rate limiter storage
    limiter.reset()
    yield

@pytest.fixture(scope="function")
async def test_db() -> AsyncIterator[AsyncIOMotorDatabase]:
    """Create a test database."""
    # Create a new client for each test
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.test_mongodb_database]

    # Clear existing data
    await client.drop_database(settings.test_mongodb_database)

    try:
        yield db
    finally:
        # Cleanup
        await client.drop_database(settings.test_mongodb_database)
        # Close the client
        client.close()

@pytest.fixture(scope="function")
async def test_presets(test_db: AsyncIOMotorDatabase) -> AsyncIterator[AsyncIOMotorDatabase]:
    """Initialize test presets in the database."""
    # Insert test data
    await test_db.chord_progressions.insert_many([
        {"name": "I-IV-V-I", "progression": ["I", "IV", "V", "I"]},
        {"name": "test_I-IV-V", "progression": ["I", "IV", "V"]}
    ])
    await test_db.note_patterns.insert_many([
        {"name": "Simple Triad", "pattern": [0, 2, 4]},
        {"name": "test_simple_triad", "pattern": [0, 2, 4]}
    ])
    await test_db.rhythm_patterns.insert_many([
        {"name": "Basic Rhythm", "pattern": [1, 1, 1, 1]},
        {"name": "test_quarter_notes", "pattern": [1, 1, 1, 1]}
    ])

    try:
        yield test_db
    finally:
        # Cleanup happens in test_db fixture
        pass

@pytest.fixture(scope="function")
async def test_client(test_db: AsyncIOMotorDatabase) -> AsyncIterator[AsyncClient]:
    """Create an async test client."""
    # Create a dependency override for the database connection
    async def override_get_db():
        yield test_db

    # Override the dependency
    app.dependency_overrides[get_db_conn] = override_get_db

    # Create the test client
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    )

    # Yield the client
    yield client

    # Clean up
    await client.aclose()
    app.dependency_overrides.clear()
