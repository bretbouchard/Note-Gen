"""Database connection module."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Any, AsyncGenerator
import logging
from contextlib import asynccontextmanager
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection settings
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = os.getenv("MONGO_DB_NAME", "note_gen")
TEST_DB_NAME = "test_note_gen"

# MongoDB connection settings
MONGO_SETTINGS = {
    'maxPoolSize': 10,
    'minPoolSize': 1,
    'maxIdleTimeMS': 30000,  # 30 seconds
    'waitQueueTimeoutMS': 5000,  # 5 seconds
    'connectTimeoutMS': 5000,
    'retryWrites': True,
    'serverSelectionTimeoutMS': 5000
}

# MongoDB client instance
_client: AsyncIOMotorClient[Any] | None = None
_db: AsyncIOMotorDatabase[Any] | None = None

async def get_client() -> AsyncIOMotorClient[Any]:
    """Get MongoDB client instance with optimized connection pooling."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL, **MONGO_SETTINGS)
        # Test connection
        try:
            await _client.admin.command('ping')
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            _client = None
            raise
    return _client

async def get_database() -> AsyncIOMotorDatabase[Any]:
    """Get database instance."""
    global _db
    if _db is None:
        try:
            client = await get_client()
            db_name = TEST_DB_NAME if os.getenv("TESTING") else DB_NAME
            print(f"Using database: {db_name}")
            print(f"Using database: {DB_NAME}")
            _db = client[db_name]
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise
    return _db

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    """Get the database connection as an async context manager."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    logger.info("Database connection established: %s", db)
    try:
        yield db
    finally:
        client.close()

async def close_mongo_connection() -> None:
    """Close database connection."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
    _db = None

async def init_database() -> None:
    """Initialize the database with collections if they don't exist."""
    if os.getenv("TESTING"):
        # Skip initialization for test database
        return
        
    async with get_db() as db:
        if "chord_progressions" not in await db.list_collection_names():
            await db.create_collection("chord_progressions")
            logger.info("Created chord_progressions collection")
            
        if "note_patterns" not in await db.list_collection_names():
            await db.create_collection("note_patterns")
            logger.info("Created note_patterns collection")
            
        if "rhythm_patterns" not in await db.list_collection_names():
            await db.create_collection("rhythm_patterns")
            logger.info("Created rhythm_patterns collection")
            
        # Import presets if collections are empty
        if not os.getenv("TESTING"):
            from src.note_gen.import_presets import import_presets_if_empty
            await import_presets_if_empty(db)
