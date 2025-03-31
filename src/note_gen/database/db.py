"""Database connection module."""
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.note_gen.core.constants import DATABASE, DB_NAME

async def get_db_conn() -> AsyncIOMotorDatabase:
    """Get database connection."""
    client = AsyncIOMotorClient(
        DATABASE["uri"],
        maxPoolSize=DATABASE["pool"]["max_size"],
        minPoolSize=DATABASE["pool"]["min_size"],
        serverSelectionTimeoutMS=DATABASE["timeout_ms"]
    )
    return client[DB_NAME]

async def get_database() -> AsyncIOMotorDatabase:
    """Alias for get_db_conn for backward compatibility."""
    return await get_db_conn()

async def init_db():
    """Initialize database connection."""
    db = await get_db_conn()
    # Add any initialization logic here
    return db

async def close_mongo_connection():
    """Close database connection."""
    client = AsyncIOMotorClient(DATABASE["uri"])
    client.close()
