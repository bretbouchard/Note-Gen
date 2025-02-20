"""
Database dependencies for FastAPI.
"""

import os
from typing import AsyncGenerator
from src.note_gen.database.db import get_db_conn as _get_db_conn
from motor.motor_asyncio import AsyncIOMotorDatabase

# Get MongoDB URI from environment
MONGODB_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

async def get_db_conn():
    """Get database connection."""
    return await _get_db_conn()

# Export for use in other modules
__all__ = ['get_db_conn', 'MONGODB_URL']