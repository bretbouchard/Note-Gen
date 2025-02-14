"""
src/note_gen/database/db.py

Database connection and dependency injection for MongoDB.
"""

import os
import asyncio
import logging
from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
from fastapi import status
from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from contextlib import asynccontextmanager

# Get MongoDB URI from environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

# For testing, use test database
if os.getenv("TESTING") == "1":
    MONGODB_URI = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")
    DATABASE_NAME = "test_note_gen"

logger = logging.getLogger(__name__)

class MongoDBConnection:
    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        self.uri = uri or MONGODB_URI
        self.db_name = db_name or DATABASE_NAME
        self.client = None
        self.db = None

    async def __aenter__(self):
        logger.debug(f"Connecting to MongoDB at {self.uri}/{self.db_name}")
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]
        logger.debug("Successfully connected to MongoDB")
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
            logger.debug("Closed MongoDB connection")

async def get_db_conn(uri: Optional[str] = None, db_name: Optional[str] = None) -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection."""
    async with MongoDBConnection(uri=uri, db_name=db_name) as db:
        yield db

async def init_db(uri: Optional[str] = None, db_name: Optional[str] = None) -> None:
    """Initialize database connection."""
    try:
        async with MongoDBConnection(uri=uri, db_name=db_name) as conn:
            await conn.command('ping')
            logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def close_mongo_connection(uri: Optional[str] = None, db_name: Optional[str] = None) -> None:
    """Close database connection."""
    try:
        logger.info("Attempting to close MongoDB connection...")
        async with MongoDBConnection(uri=uri, db_name=db_name) as conn:
            if conn.client:
                conn.client.close()
                logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")
        raise
