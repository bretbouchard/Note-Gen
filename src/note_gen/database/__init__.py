"""Database initialization module."""
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from note_gen.core.constants import DATABASE

# Initialize the MongoDB client
# Cast DATABASE to Dict[str, Any] to help mypy understand the type
db_config: Dict[str, Any] = DATABASE
client: AsyncIOMotorClient = AsyncIOMotorClient(str(db_config.get("uri", "mongodb://localhost:27017")))
db: AsyncIOMotorDatabase = client[str(db_config.get("name", "note_gen"))]

async def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    return db
