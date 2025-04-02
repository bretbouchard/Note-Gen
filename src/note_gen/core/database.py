"""Database connection and management."""
from typing import Optional, Dict, Any, cast
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .constants import DATABASE

_db_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def get_database() -> AsyncIOMotorDatabase:
    """Get database connection."""
    global _db_client, _db

    if _db is None:
        # Cast DATABASE to Dict[str, Any] to help mypy understand the type
        db_config = cast(Dict[str, Any], DATABASE)

        _db_client = AsyncIOMotorClient(
            str(db_config["uri"]),
            maxPoolSize=int(db_config["pool"]["max_size"]),
            minPoolSize=int(db_config["pool"]["min_size"]),
            serverSelectionTimeoutMS=int(db_config.get("timeout_ms", 5000))
        )
        _db = _db_client[str(db_config["name"])]

    return _db

# Alias for backward compatibility
get_db_conn = get_database

async def close_database() -> None:
    """Close database connection."""
    global _db_client, _db
    if _db_client is not None:
        _db_client.close()
        _db_client = None
        _db = None
