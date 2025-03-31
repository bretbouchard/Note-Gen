"""Database dependency module."""
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..database.db import get_db_conn

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Database dependency."""
    db = await get_db_conn()
    try:
        yield db
    finally:
        # Connection cleanup if needed
        pass
