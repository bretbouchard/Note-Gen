# in dependencies.py
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

MONGODB_URL = "mongodb://localhost:27017/"

def get_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(MONGODB_URL)
    return client.note_gen