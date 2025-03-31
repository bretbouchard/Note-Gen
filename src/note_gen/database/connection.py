"""Database connection management."""

from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.note_gen.core.constants import DATABASE, DEFAULT_DB_NAME

async def get_database_connection() -> AsyncIOMotorDatabase[Any]:
    """Get database connection."""
    client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(
        DATABASE["uri"],  # Use the URI from the DATABASE constant
        serverSelectionTimeoutMS=DATABASE["timeout_ms"],
        maxPoolSize=DATABASE["pool"]["max_size"],
        minPoolSize=DATABASE["pool"]["min_size"]
    )
    return client[DEFAULT_DB_NAME]
