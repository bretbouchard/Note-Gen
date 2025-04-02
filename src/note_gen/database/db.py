"""Database connection management."""
from motor.motor_asyncio import AsyncIOMotorClient
from ..config import settings

_client = None

async def init_db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_url)
    return _client

async def get_db_conn():
    if _client is None:
        await init_db()
    return _client[settings.database_name]

async def close_mongo_connection():
    global _client
    if _client is not None:
        _client.close()
        _client = None
