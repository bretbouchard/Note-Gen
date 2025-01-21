from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from pymongo import MongoClient
from typing import Dict, Any

# Database connection settings
MONGODB_URL = "mongodb://localhost:27017/"

# Dependency to get the database instance
async def get_db() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.note_gen
    try:
        yield db
    finally:
        client.close()
