"""Database connection management."""

from motor.motor_asyncio import AsyncIOMotorClient
from src.note_gen.core.constants import (
    DEFAULT_MONGODB_URI,
    DEFAULT_DB_NAME,
    DEFAULT_CONNECTION_TIMEOUT_MS,
    MAX_POOL_SIZE,
    MIN_POOL_SIZE
)

async def get_database_connection():
    client = AsyncIOMotorClient(
        DEFAULT_MONGODB_URI,
        serverSelectionTimeoutMS=DEFAULT_CONNECTION_TIMEOUT_MS,
        maxPoolSize=MAX_POOL_SIZE,
        minPoolSize=MIN_POOL_SIZE
    )
    return client[DEFAULT_DB_NAME]
