"""
Database connection and dependency injection for MongoDB.
"""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import AsyncGenerator

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

# For testing, use test database
if os.getenv("TESTING") == "1":
    MONGODB_URI = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")
    DATABASE_NAME = "test_note_gen"

# Global connection instance - made per event loop
_clients = {}
_dbs = {}

MONGODB_SETTINGS = {
    'serverSelectionTimeoutMS': 5000,  # 5 seconds timeout
    'connectTimeoutMS': 5000,
    'socketTimeoutMS': 5000,
}

class AsyncDBConnection:
    """Async database connection manager that ensures we use the correct event loop."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.loop_id = None

    async def __aenter__(self) -> AsyncIOMotorDatabase:
        """Initialize database connection on the current event loop."""
        global _clients, _dbs
        
        # Get current event loop
        current_loop = asyncio.get_running_loop()
        self.loop_id = id(current_loop)
        
        try:
            # Check if we already have a connection for this loop
            if self.loop_id in _clients and _clients[self.loop_id] is not None:
                logger.debug(f"Reusing existing MongoDB connection for loop {self.loop_id}")
                self.client = _clients[self.loop_id]
                self.db = _dbs[self.loop_id]
            else:
                # Create a new connection for this loop
                logger.debug(f"Connecting to MongoDB at {MONGODB_URI}/{DATABASE_NAME} on loop {self.loop_id}")
                self.client = AsyncIOMotorClient(MONGODB_URI)
                self.db = self.client[DATABASE_NAME]
                
                # Store in our global registry for this loop
                _clients[self.loop_id] = self.client
                _dbs[self.loop_id] = self.db
                
                logger.debug(f"Successfully connected to MongoDB on loop {self.loop_id}")
            
            return self.db
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB on loop {self.loop_id}: {str(e)}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - keep connection alive."""
        pass

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    client = AsyncIOMotorClient(
        MONGODB_URI,
        **MONGODB_SETTINGS
    )
    try:
        yield client[DATABASE_NAME]
    finally:
        client.close()

async def get_db_conn() -> AsyncIOMotorDatabase:
    """Get database connection."""
    async with get_db() as db:
        return db

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
    global _clients, _dbs
    
    # Get current event loop
    try:
        current_loop = asyncio.get_running_loop()
        loop_id = id(current_loop)
        
        if loop_id in _clients and _clients[loop_id] is not None:
            logger.debug(f"Closing MongoDB connection for loop {loop_id}")
            _clients[loop_id].close()
            _clients[loop_id] = None
            _dbs[loop_id] = None
            logger.info(f"MongoDB connection closed successfully for loop {loop_id}")
    except RuntimeError:
        # No running event loop, we might be shutting down
        # Close all connections
        logger.debug("No running event loop, closing all connections")
        for loop_id, client in _clients.items():
            if client is not None:
                client.close()
                _clients[loop_id] = None
                _dbs[loop_id] = None
        logger.info("All MongoDB connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")
        raise

async def drop_database():
    if current_app.database:
        await current_app.database.client.drop_database(current_app.database.name)
        logger.info(f"Dropped database: {current_app.database.name}")