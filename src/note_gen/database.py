"""Database connection module."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get a database connection."""
    client = None
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Create client and yield database
        client = AsyncIOMotorClient('mongodb://localhost:27017', io_loop=loop)
        yield client.note_gen
    finally:
        if client:
            client.close()

async def init_database() -> None:
    """Initialize the database with collections if they don't exist."""
    async with get_db() as db:
        if "chord_progressions" not in await db.list_collection_names():
            await db.create_collection("chord_progressions")
            await db.chord_progressions.create_index("name", unique=True)
        
        if "note_patterns" not in await db.list_collection_names():
            await db.create_collection("note_patterns")
            await db.note_patterns.create_index("name", unique=True)
        
        if "rhythm_patterns" not in await db.list_collection_names():
            await db.create_collection("rhythm_patterns")
            await db.rhythm_patterns.create_index("name", unique=True)
        
        logger.info("Database initialized successfully")
