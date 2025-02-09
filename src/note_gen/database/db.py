"""
src/note_gen/database/db.py

Database connection and dependency injection for MongoDB.
"""

import os
import asyncio
import logging
from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends

# Get MongoDB URI from environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

# For testing, use test database
if os.getenv("TESTING") == "1":
    MONGODB_URI = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")
    DATABASE_NAME = "note_gen_test"

logger = logging.getLogger(__name__)

# Global client variable
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def init_db() -> AsyncIOMotorDatabase:
    """Initialize database connection."""
    global _client, _db
    if _client is None:
        logger.info("Initializing MongoDB connection...")
        try:
            _client = AsyncIOMotorClient(MONGODB_URI)
            _db = _client[DATABASE_NAME]
            # Test the connection
            await _db.command('ping')
            logger.info("Successfully connected to MongoDB")
            return _db
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    return _db

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection."""
    global _db
    if _db is None:
        _db = await init_db()
    try:
        yield _db
    finally:
        # Don't close connection here, it's handled by close_mongo_connection
        pass

async def close_mongo_connection() -> None:
    """Close database connection."""
    global _client, _db
    if _client is not None:
        logger.info("Closing MongoDB connection...")
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")

# Export MONGODB_URI as MONGO_URL
MONGO_URL = MONGODB_URI
