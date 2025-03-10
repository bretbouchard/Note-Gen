"""Database connection module."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from motor import motor_asyncio
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.patterns import NotePattern, RhythmPattern
from typing import Any, AsyncGenerator, Dict, List, Optional
import logging
from contextlib import asynccontextmanager
import atexit
import os
import threading
import traceback
from fastapi import HTTPException

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
    'maxPoolSize': 10,  # Ensure this is an integer
    'minPoolSize': 1,   # Ensure this is an integer
    'maxIdleTimeMS': 30000,  # Ensure this is an integer (30 seconds)
    'waitQueueTimeoutMS': 5000,  # Ensure this is an integer (5 seconds)
    'connectTimeoutMS': 5000,  # Ensure this is an integer (5 seconds)
    'retryWrites': True,  # Ensure this is a boolean
    'serverSelectionTimeoutMS': 5000  # Ensure this is an integer (5 seconds)
}

# Global variables
_client: Optional[AsyncIOMotorClient[Any]] = None
_db: Optional[AsyncIOMotorDatabase[Any]] = None


async def get_client() -> AsyncIOMotorClient[Any]:
    global _client
    if _client is None:
        try:
            _client = AsyncIOMotorClient(
                MONGO_URL,
                **MONGO_SETTINGS  
            )
            await _client.admin.command('ping')
            logger.info("MongoDB connection established.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
            raise
    return _client

async def get_db() -> AsyncIOMotorDatabase[Any]:
    global _db
    if _db is None:
        client = await get_client()
        db_name = TEST_DB_NAME if os.getenv("TESTING") else DB_NAME
        _db = client[db_name]
        logger.info(f"Successfully connected to database: {db_name}")
    return _db

async def close_mongo_connection() -> None:
    global _client, _db
    if _client:
        try:
            _client.close()
            logger.info("MongoDB connection closed.")
        except Exception as e:
            logger.error(f"Failed to close MongoDB connection: {e}", exc_info=True)
        finally:
            _client = None
            _db = None

async def init_database() -> None:
    """Initialize the database with collections if they don't exist."""
    if os.getenv("TESTING"):
        logger.debug("Skipping database initialization for testing.")
        return
    db = await get_db()
    logger.debug("Initializing database collections...")
    try:
        if "chord_progressions" not in await db.list_collection_names():
            await db.create_collection("chord_progressions")
            logger.info("Created chord_progressions collection")
        else:
            logger.info("chord_progressions collection already exists")
        if "note_patterns" not in await db.list_collection_names():
            await db.create_collection("note_patterns")
            logger.info("Created note_patterns collection")
        else:
            logger.info("note_patterns collection already exists")
        if "rhythm_patterns" not in await db.list_collection_names():
            await db.create_collection("rhythm_patterns")
            logger.info("Created rhythm_patterns collection")
        else:
            logger.info("rhythm_patterns collection already exists")
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
        db = await get_db()
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
        # Convert complex model to dictionary, handling nested models
        prog_dict = progression.model_dump()
        
        # Convert nested Note and Chord models to dictionaries
        if 'chords' in prog_dict:
            prog_dict['chords'] = [
                {
                    'root': {
                        'note_name': chord.get('root', {}).get('note_name', ''),
                        'octave': chord.get('root', {}).get('octave', 4)
                    },
                    'quality': chord.get('quality', '')
                } for chord in prog_dict['chords']
            ]
        
        # Convert scale_info if present
        if 'scale_info' in prog_dict:
            prog_dict['scale_info'] = {
                'root': {
                    'note_name': prog_dict['scale_info'].get('root', {}).get('note_name', ''),
                    'octave': prog_dict['scale_info'].get('root', {}).get('octave', 4)
                },
                'scale_type': prog_dict['scale_info'].get('scale_type', '')
            }
        
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
        logger.error(f"Error creating chord progression: {e}")
        logger.error(traceback.format_exc())
        logger.error(f"Progression data: {prog_dict}")
        raise HTTPException(status_code=500, detail=str(e))

async def create_note_pattern(db: AsyncIOMotorDatabase, note_pattern: NotePattern) -> Dict[str, Any]:
    logger.debug("Attempting to create note pattern...")
    try:
        # Convert complex model to dictionary
        pattern_dict = note_pattern.model_dump()
        
        # Simplify nested models if needed
        if 'pattern' in pattern_dict:
            pattern_dict['pattern'] = list(pattern_dict['pattern'])
        
        if 'notes' in pattern_dict:
            pattern_dict['notes'] = [
                {
                    'note_name': note.get('note_name', ''),
                    'octave': note.get('octave', 4),
                    'duration': note.get('duration', 1),
                    'velocity': note.get('velocity', 100)
                } for note in pattern_dict['notes']
            ]
        
        logger.debug(f"Note pattern data to insert: {pattern_dict}")
        result = await db.note_patterns.insert_one(pattern_dict)
        logger.debug(f"Insert result: {result}")
        
        if result.inserted_id:
            created_pattern = await db.note_patterns.find_one({"_id": result.inserted_id})
            if created_pattern:
                created_pattern["id"] = str(created_pattern.pop("_id"))
                logger.info(f"Successfully created note pattern: {created_pattern}")
                return created_pattern
        
        raise HTTPException(status_code=500, detail="Failed to create note pattern")
    except Exception as e:
        logger.error(f"Error creating note pattern: {e}")
        logger.error(traceback.format_exc())
        logger.error(f"Note pattern data: {pattern_dict}")
        raise HTTPException(status_code=500, detail=str(e))

async def create_rhythm_pattern(db: AsyncIOMotorDatabase, rhythm_pattern: RhythmPattern) -> Dict[str, Any]:
    logger.debug("Attempting to create rhythm pattern...")
    try:
        # Convert complex model to dictionary
        pattern_dict = rhythm_pattern.model_dump()
        
        # Simplify nested models if needed
        if 'data' in pattern_dict:
            pattern_dict['data'] = {
                'notes': [
                    {
                        'position': note.get('position', 0.0),
                        'duration': note.get('duration', 1.0),
                        'velocity': note.get('velocity', 100),
                        'is_rest': note.get('is_rest', False)
                    } for note in pattern_dict['data'].get('notes', [])
                ],
                'time_signature': pattern_dict['data'].get('time_signature', '4/4'),
                'swing_ratio': pattern_dict['data'].get('swing_ratio', 0.67),
                'default_duration': pattern_dict['data'].get('default_duration', 1.0),
                'total_duration': pattern_dict['data'].get('total_duration', 4.0),
                'groove_type': pattern_dict['data'].get('groove_type', 'straight'),
                'variation_probability': pattern_dict['data'].get('variation_probability', 0.0),
                'duration': pattern_dict['data'].get('duration', 4.0)
            }
        
        logger.debug(f"Rhythm pattern data to insert: {pattern_dict}")
        result = await db.rhythm_patterns.insert_one(pattern_dict)
        logger.debug(f"Insert result: {result}")
        
        if result.inserted_id:
            created_pattern = await db.rhythm_patterns.find_one({"_id": result.inserted_id})
            if created_pattern:
                created_pattern["id"] = str(created_pattern.pop("_id"))
                logger.info(f"Successfully created rhythm pattern: {created_pattern}")
                return created_pattern
        
        raise HTTPException(status_code=500, detail="Failed to create rhythm pattern")
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}")
        logger.error(traceback.format_exc())
        logger.error(f"Rhythm pattern data: {pattern_dict}")
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