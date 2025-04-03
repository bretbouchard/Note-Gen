"""Database connection management."""

from typing import Any, Dict, cast
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from note_gen.core.constants import DATABASE

async def get_database_connection() -> AsyncIOMotorDatabase:
    """Get database connection."""
    # Cast DATABASE to Dict[str, Any] to help mypy understand the type
    db_config = cast(Dict[str, Any], DATABASE)

    client: AsyncIOMotorClient = AsyncIOMotorClient(
        str(db_config.get("uri", "mongodb://localhost:27017")),
        serverSelectionTimeoutMS=int(db_config.get("timeout_ms", 5000)),
        maxPoolSize=int(db_config.get("pool", {}).get("max_size", 10)),
        minPoolSize=int(db_config.get("pool", {}).get("min_size", 1))
    )
    return client[str(db_config.get("name", "note_gen"))]
