"""Test fixtures for database tests."""

import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.note_gen.database.transaction import TransactionManager

@pytest.fixture
async def mongodb_client():
    """Create a MongoDB client for testing."""
    client = AsyncIOMotorClient(
        "mongodb://localhost:27017",
        # Disable transactions for testing with standalone MongoDB
        directConnection=True   
    )
    try:
        # Test the connection
        await client.admin.command('ping')
        yield client
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")
    finally:
        if client:
            await client.drop_database("note_gen_db_dev")
            client.close()

@pytest.fixture
async def mongodb_collection(mongodb_client):
    """Create a test collection."""
    db = mongodb_client["note_gen_db_dev_db"]
    collection = db["test_collection"]
    await collection.delete_many({})  # Clean up before test
    return collection

@pytest.fixture
async def transaction_manager(mongodb_client):
    """Create a transaction manager for testing."""
    return TransactionManager(mongodb_client)


