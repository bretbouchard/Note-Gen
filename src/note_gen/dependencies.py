"""
Database dependencies for FastAPI.
"""

import os
import asyncio
import logging
from typing import AsyncGenerator
from src.note_gen.database.db import get_db_conn as _get_db_conn
from motor.motor_asyncio import AsyncIOMotorDatabase

# Configure logging
logger = logging.getLogger(__name__)

# Get MongoDB URI from environment
MONGODB_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017") 
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

async def get_db_conn() -> AsyncIOMotorDatabase:
    """
    Get database connection.
    
    This wraps the original get_db_conn function to ensure it 
    uses the current event loop and adds error handling.
    """
    try:
        logger.debug("Getting database connection with current event loop")
        # Try to get from current loop first
        try:
            # Get the current loop
            current_loop = asyncio.get_running_loop()
            
            # Import the AsyncDBConnection to get a fresh connection on this loop
            from src.note_gen.database.db import AsyncDBConnection
            
            # Create a new connection with the current loop
            async with AsyncDBConnection() as db:
                return db
        except Exception as e:
            # Fall back to original function
            logger.warning(f"Falling back to original get_db_conn due to: {e}")
            return await _get_db_conn()
    except RuntimeError as e:
        if "Task got Future" in str(e) and "attached to a different loop" in str(e):
            logger.warning("Event loop mismatch detected, reestablishing connection")
            
            # Get the current loop
            current_loop = asyncio.get_running_loop()
            
            # Import the AsyncDBConnection to get a fresh connection on this loop
            from src.note_gen.database.db import AsyncDBConnection
            
            # Create a new connection with the current loop
            async with AsyncDBConnection() as db:
                return db
        else:
            # Reraise other RuntimeErrors
            logger.error(f"Error getting database connection: {e}")
            raise

# Export for use in other modules
__all__ = ['get_db_conn', 'MONGODB_URL']