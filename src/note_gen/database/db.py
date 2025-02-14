"""
src/note_gen/database/db.py

Database connection and dependency injection for MongoDB.
"""

import os
import asyncio
import logging
from typing import Optional, AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
from fastapi import status
from pymongo import MongoClient
from pymongo.errors import ConfigurationError

# Get MongoDB URI from environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

# For testing, use test database
if os.getenv("TESTING") == "1":
    MONGODB_URI = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")
    DATABASE_NAME = "test_note_gen"

logger = logging.getLogger(__name__)

_client: Optional[AsyncIOMotorClient] = None

class AsyncDBConnection:
    """Async database connection context manager."""
    def __init__(self):
        self.client = None
        self.db = None

    async def __aenter__(self):
        """Get database connection."""
        global _client
        if _client is None:
            logger.debug(f"Connecting to MongoDB at {MONGODB_URI}/{DATABASE_NAME}")
            _client = AsyncIOMotorClient(MONGODB_URI)
            logger.debug("Successfully connected to MongoDB")
        self.client = _client
        self.db = self.client[DATABASE_NAME]
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close database connection."""
        if self.client:
            logger.info("Attempting to close MongoDB connection...")
            self.client.close()
            global _client
            _client = None
            logger.info("MongoDB connection closed successfully")

def get_db_conn() -> AsyncDBConnection:
    """Get database connection context manager."""
    return AsyncDBConnection()

async def init_db() -> None:
    """Initialize database connection."""
    try:
        db = get_db_conn()
        async with db as conn:
            await conn.command('ping')
            logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def close_mongo_connection() -> None:
    """Close database connection."""
    global _client
    
    try:
        logger.info("Attempting to close MongoDB connection...")
        if _client:
            _client.close()
            _client = None
            logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")
        raise
