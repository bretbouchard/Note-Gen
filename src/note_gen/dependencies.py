"""FastAPI dependencies."""
from typing import AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

# Use consistent import style
from note_gen.database.db import get_db_conn, close_mongo_connection

async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection dependency."""
    async for db in get_db_conn():
        yield db
