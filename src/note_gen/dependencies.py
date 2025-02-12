# in dependencies.py
from typing import Any
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.note_gen.database import get_db_connection

MONGODB_URL = "mongodb://localhost:27017/"
client = AsyncIOMotorClient(MONGODB_URL)

async def get_db() -> AsyncIOMotorDatabase:
    """
    Get database connection.
    
    Uses get_db_connection to ensure a proper database connection.
    """
    return await get_db_connection()