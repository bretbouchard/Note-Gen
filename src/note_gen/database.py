"""Database connection module."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from motor import motor_asyncio
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern
from typing import Any, AsyncGenerator, Dict, List, Optional
import logging
from contextlib import asynccontextmanager
import atexit
import os
import threading
import traceback

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.getLogger("pymongo").setLevel(logging.WARNING)

# MongoDB connection settings
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = os.getenv("MONGO_DB_NAME", "note_gen")
TEST_DB_NAME = "test_note_gen"

# MongoDB connection settings
MONGO_SETTINGS = {
    'maxPoolSize': 10,
    'minPoolSize': 1,
    'maxIdleTimeMS': 30000,  # 30 seconds
    'waitQueueTimeoutMS': 5000,  # 5 seconds
    'connectTimeoutMS': 5000,
    'retryWrites': True,
    'serverSelectionTimeoutMS': 5000
}

# Global variables
_client_lock = threading.Lock()
_client: AsyncIOMotorClient[Any] | None = None
_db: AsyncIOMotorDatabase[Any] | None = None


async def get_client() -> AsyncIOMotorClient[Any]:
    global _client
    with _client_lock:
        if _client is None:
            logger.debug("Initializing MongoDB client...")
            logger.debug(f"Connecting to MongoDB at {MONGO_URL}")
            try:
                _client = AsyncIOMotorClient(
                    MONGO_URL,
                    **MONGO_SETTINGS  
                )
                await _client.admin.command('ping')
                logger.info("MongoDB connection established.")
                logger.debug(f"Client initialized: {_client}")  
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
                if _client:
                    _client.close()
                _client = None
                raise
    logger.debug(f"Returning client: {_client}")  
    return _client

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    global _client, _db
    if _db is None:
        logger.debug("Getting database instance...")
        try:
            client = await get_client()
            db_name = TEST_DB_NAME if os.getenv("TESTING") else DB_NAME
            logger.debug(f"Using database: {db_name}")
            _db = client[db_name]
            logger.info(f"Successfully connected to database: {db_name}")
            logger.debug(f"Database instance: {_db}")
            logger.debug(f"_db is initialized: {_db is not None}")
        except Exception as e:
            logger.error(f"Failed to retrieve database instance: {e}", exc_info=True)
            raise
    else:
        logger.debug("Using existing database instance.")
        logger.debug(f"_db is initialized: {_db is not None}")
    try:
        logger.debug("Yielding database instance...")
        yield _db
    except Exception as e:
        logger.error(f"Error occurred while using database: {e}", exc_info=True)
    finally:
        logger.debug("Database connection yielded.")

# Modify close_mongo_connection
async def close_mongo_connection() -> None:
    global _client, _db
    with _client_lock:
        if isinstance(_client, AsyncIOMotorClient):  
            try:
                logger.info("Closing MongoDB connection...")
                _client.close()  
                logger.info("MongoDB connection closed.")
            except Exception as e:
                logger.error(f"Failed to close MongoDB connection: {e}", exc_info=True)
            finally:
                _client = None
                _db = None
        else:
            logger.warning("_client is not a valid AsyncIOMotorClient instance.")

async def init_database() -> None:
    """Initialize the database with collections if they don't exist."""
    if os.getenv("TESTING"):
        logger.debug("Skipping database initialization for testing.")
        return
    async with get_db() as db:
        logger.debug("Initializing database collections...")
        try:
            if "chord_progressions" not in await db.list_collection_names():
                await db.create_collection("chord_progressions")
                logger.info("Created chord_progressions collection")
            if "note_patterns" not in await db.list_collection_names():
                await db.create_collection("note_patterns")
                logger.info("Created note_patterns collection")
            if "rhythm_patterns" not in await db.list_collection_names():
                await db.create_collection("rhythm_patterns")
                logger.info("Created rhythm_patterns collection")
        except Exception as e:
            logger.error(f"Failed to initialize database collections: {e}", exc_info=True)
        else:
            # Import presets if collections are empty
            if not os.getenv("TESTING"):
                from src.note_gen.import_presets import import_presets_if_empty
                await import_presets_if_empty(db)

async def init_db():
    """Initialize database connection."""
    global _client, _db
    try:
        await get_client()
        async with get_db() as db:
            _db = db
            await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def close_db():
    """Close database connection."""
    global _client, _db
    if _client:
        await close_mongo_connection()
        _client = None
        _db = None
        logger.info("Database connection closed")

async def create_chord_progression(db: AsyncIOMotorDatabase, progression: ChordProgression) -> Dict[str, Any]:
    logger.debug("Attempting to create chord progression...")
    try:
        prog_dict = progression.model_dump()
        logger.debug(f"Chord progression data to insert: {prog_dict}")
        result = await db.chord_progressions.insert_one(prog_dict)
        logger.debug(f"Insert result: {result}")
        if result.inserted_id:
            created_progression = await db.chord_progressions.find_one({"_id": result.inserted_id})
            if created_progression:
                created_progression["id"] = str(created_progression.pop("_id"))
                logger.info(f"Successfully created chord progression: {created_progression}")
                return created_progression
        raise HTTPException(status_code=500, detail="Failed to create chord progression")
    except Exception as e:
        logger.error(f"Error creating chord progression: {e}")  # Log the exception message
        logger.error(traceback.format_exc())  # Log the full traceback
        logger.error(f"Progression data: {prog_dict}")  # Log the progression data
        raise HTTPException(status_code=500, detail=str(e))

async def get_chord_progressions(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    try:
        cursor = db.chord_progressions.find({})
        progressions = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            progressions.append(doc)
        return progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_chord_progression_by_name(name: str, db: motor_asyncio.AsyncIOMotorDatabase) -> Optional[ChordProgression]:
    chord_progression = await db.chord_progressions.find_one({"name": name})
    return chord_progression

async def get_note_pattern_by_name(name: str, db: motor_asyncio.AsyncIOMotorDatabase) -> Optional[NotePattern]:
    note_pattern = await db.note_patterns.find_one({"name": name})
    return note_pattern

async def get_rhythm_pattern_by_name(name: str, db: motor_asyncio.AsyncIOMotorDatabase) -> Optional[RhythmPattern]:
    rhythm_pattern = await db.rhythm_patterns.find_one({"name": name})
    return rhythm_pattern