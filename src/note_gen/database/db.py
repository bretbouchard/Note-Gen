"""Database connection management."""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..config import settings

_client: Optional[AsyncIOMotorClient] = None

async def init_db() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_url)
    return _client

async def get_db_conn() -> AsyncIOMotorDatabase:
    global _client
    if _client is None:
        await init_db()
    if _client is not None:  # Add null check for mypy
        return _client[settings.database_name]
    raise ConnectionError("Failed to initialize database connection")


async def get_database() -> AsyncIOMotorDatabase:
    """Alias for get_db_conn for compatibility with services."""
    return await get_db_conn()

async def close_mongo_connection() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
