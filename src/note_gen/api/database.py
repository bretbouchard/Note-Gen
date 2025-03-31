"""Database connection management for the API."""
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends
from ..core.constants import DATABASE

# Create a motor client
client = AsyncIOMotorClient(DATABASE["uri"])
database = client[DATABASE["name"]]

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection."""
    try:
        yield database
    finally:
        # Connection cleanup can be added here if needed
        pass

# Dependency for FastAPI
async def get_database(db: AsyncIOMotorDatabase = Depends(get_db)) -> AsyncIOMotorDatabase:
    """Database dependency."""
    return db