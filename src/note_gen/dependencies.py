"""
Database dependencies for FastAPI.
"""

import os
from typing import AsyncGenerator
from src.note_gen.database.db import MongoDBConnection
from motor.motor_asyncio import AsyncIOMotorDatabase

# Get MongoDB URI from environment
MONGODB_URL = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "note_gen")

async def get_db_conn(uri: str = None, db_name: str = None) -> AsyncIOMotorDatabase:
    """Get database connection."""
    uri = uri or MONGODB_URL
    db_name = db_name or DATABASE_NAME
    conn = MongoDBConnection(uri=uri, db_name=db_name)
    db = await conn.__aenter__()
    return db

# Export for use in other modules
__all__ = ['get_db_conn', 'MONGODB_URL']