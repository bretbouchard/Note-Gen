"""Database connection and management."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .constants import DATABASE

_db_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def get_database() -> AsyncIOMotorDatabase:
    """Get database connection."""
    global _db_client, _db
    
    if _db is None:
        _db_client = AsyncIOMotorClient(
            DATABASE["uri"],
            maxPoolSize=DATABASE["pool"]["max_size"],
            minPoolSize=DATABASE["pool"]["min_size"],
            serverSelectionTimeoutMS=DATABASE["timeout_ms"]
        )
        _db = _db_client[DATABASE["name"]]
    
    return _db

# Alias for backward compatibility
get_db_conn = get_database

async def close_database():
    """Close database connection."""
    global _db_client, _db
    if _db_client is not None:
        _db_client.close()
        _db_client = None
        _db = None
