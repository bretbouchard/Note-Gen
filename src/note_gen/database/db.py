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
    global _client, _db
    logger.info("Initializing MongoDB connection...")
    if _client is None:
        try:
            _client = AsyncIOMotorClient(MONGODB_URI)
            await _db.command('ping')
            logger.info("MongoDB connection initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}")
            raise

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection."""
    global _db
    if _db is None:
        _db = await init_db()
    try:
        logger.debug("Yielding database connection")
        yield _db
    finally:
        # Don't close connection here, it's handled by close_mongo_connection
        logger.debug("Database connection yielded")

async def get_db_connection() -> AsyncIOMotorDatabase:
    """Get database connection, ensuring it is initialized."""
    global _db
    if _db is None:
        _db = await init_db()
    logger.debug("Returning database connection")
    return _db

async def close_mongo_connection() -> None:
    global _client, _db
    logger.info("Closing MongoDB connection...")
    if _client is not None:
        try:
            _client.close()
            _client = None
            logger.info("MongoDB connection closed successfully.")
        except Exception as e:
            logger.error(f"Failed to close MongoDB connection: {e}")
            raise

# Export MONGODB_URI as MONGO_URL
MONGO_URL = MONGODB_URI
