"""Database connection and initialization."""

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import AsyncGenerator
import logging
from src.note_gen.core.constants import DATABASE, COLLECTION_NAMES

logger = logging.getLogger(__name__)

async def get_database() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database connection."""
    client: AsyncIOMotorClient = AsyncIOMotorClient(
        os.getenv("MONGODB_URI", str(DATABASE.get("uri", "mongodb://localhost:27017")))
    )
    try:
        db: AsyncIOMotorDatabase = client[os.getenv("DB_NAME", str(DATABASE.get("name", "note_gen")))]
        yield db
    finally:
        client.close()

async def init_database(db: AsyncIOMotorDatabase) -> None:
    """Initialize database with required collections and indexes."""
    try:
        # Create collections if they don't exist
        for collection_name in COLLECTION_NAMES.values():
            if collection_name not in await db.list_collection_names():
                await db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")

        # Create indexes
        await db[COLLECTION_NAMES["chord_progressions"]].create_index("name", unique=True)
        await db[COLLECTION_NAMES["note_patterns"]].create_index("name", unique=True)
        await db[COLLECTION_NAMES["rhythm_patterns"]].create_index("name", unique=True)

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

