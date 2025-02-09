# in dependencies.py
from typing import AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

MONGODB_URL = "mongodb://localhost:27017/"
client = AsyncIOMotorClient(MONGODB_URL)

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    try:
        yield client.note_gen
    finally:
        pass  # Connection is managed by the global client