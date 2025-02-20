"""
Database connection and dependency injection for MongoDB.
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

# For testing, use test database
if os.getenv("TESTING") == "1":
    MONGODB_URI = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")
    DATABASE_NAME = "test_note_gen"

# Global connection instance
_client = None
_db = None

class AsyncDBConnection:
    """Async database connection manager."""
    
    def __init__(self):
        self.client = None
        self.db = None

    async def __aenter__(self) -> AsyncIOMotorDatabase:
        """Initialize database connection."""
        global _client, _db
        try:
            if _client is None:
                logger.debug(f"Connecting to MongoDB at {MONGODB_URI}/{DATABASE_NAME}")
                _client = AsyncIOMotorClient(MONGODB_URI)
                _db = _client[DATABASE_NAME]
                logger.debug("Successfully connected to MongoDB")
            
            self.client = _client
            self.db = _db
            return self.db
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - keep connection alive."""
        pass

async def get_db_conn() -> AsyncIOMotorDatabase:
    """Get database connection."""
    global _db
    if _db is None:
        async with AsyncDBConnection() as db:
            _db = db
    return _db

async def init_db() -> None:
    """Initialize database connection."""
    try:
        db = await get_db_conn()
        await db.command('ping')
        logger.info("Database connection initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def close_mongo_connection() -> None:
    """Close database connection during application shutdown."""
    global _client, _db
    try:
        if _client:
            _client.close()
            _client = None
            _db = None
            logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")
        raise