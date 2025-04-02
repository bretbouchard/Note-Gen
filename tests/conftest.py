"""Root test configuration and fixtures."""
import pytest
import asyncio
import os

# Ensure test environment
os.environ["TESTING"] = "1"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Don't close the loop here to avoid 'Event loop is closed' errors

import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import AsyncIterator
from src.note_gen.config import settings

@pytest_asyncio.fixture
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
