"""
Database dependencies for FastAPI.
"""

import logging
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase
from .database.db import get_db_conn, close_mongo_connection

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection."""
    logger.debug("Getting database connection with current event loop")
    db = await get_db_conn()
    try:
        yield db
    finally:
        await close_mongo_connection()
