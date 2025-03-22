"""
Database connection and dependency injection for MongoDB.
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, AsyncGenerator
import os

logger = logging.getLogger(__name__)

# Database configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "test_note_gen")

# Global client instance
_client: Optional[AsyncIOMotorClient] = None

async def get_db_conn(uri: str = MONGODB_URI, db_name: str = DATABASE_NAME) -> AsyncIOMotorDatabase:
    """Get database connection."""
    global _client
    
    if _client is None:
        logger.debug(f"Creating new MongoDB connection to {uri}")
        _client = AsyncIOMotorClient(uri)
        
        # Test the connection
        try:
            await _client.admin.command('ping')
            logger.debug("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    return _client[db_name]

async def close_mongo_connection() -> None:
    """Close the database connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.debug("Closed MongoDB connection")

class AsyncDBConnection:
    """Async context manager for database connections."""
    
    def __init__(self, uri: str = MONGODB_URI, db_name: str = DATABASE_NAME):
        self.uri = uri
        self.db_name = db_name
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def __aenter__(self) -> AsyncIOMotorDatabase:
        self.db = await get_db_conn(self.uri, self.db_name)
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await close_mongo_connection()

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Database dependency for FastAPI."""
    db = await get_db_conn()
    try:
        yield db
    finally:
        await close_mongo_connection()

async def init_db(db: AsyncIOMotorDatabase = None) -> None:
    """Initialize database with required collections."""
    if db is None:
        db = await get_db_conn()
    
    # Create collections if they don't exist
    collections = await db.list_collection_names()
    required_collections = [
        "chord_progressions",
        "note_patterns",
        "rhythm_patterns"
    ]
    
    for collection in required_collections:
        if collection not in collections:
            await db.create_collection(collection)
            logger.debug(f"Created collection: {collection}")

async def get_database():
    """Get database instance."""
    client = await get_db_conn()
    return client[DATABASE_NAME]

# Make sure to export these in __init__.py
__all__ = [
    'get_db_conn',
    'close_mongo_connection',
    'AsyncDBConnection',
    'get_db',
    'init_db',
    'MONGODB_URI',
    'DATABASE_NAME'
]
