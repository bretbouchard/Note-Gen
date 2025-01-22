"""Module for importing preset data into MongoDB."""

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.database import Database
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.rhythm_pattern import RhythmPatternData
from typing import Any, Optional, Dict

# MongoDB connection setup
async def initialize_client():
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://localhost:27017/")
        logger.info("MongoDB client initialized.")
        logger.info(f"MongoDB client connected to {client.address}")
        logger.info(f"MongoDB client server info: {client.server_info()}")
        async def get_database_names():
            return await client.list_database_names()
        logger.info(f"MongoDB client database names: {await get_database_names()}")
        logger.info(f"MongoDB client connection pool size: {client.maxPoolSize}")
        logger.info(f"MongoDB client connection timeout: {client.local_threshold}")
        return client
    except ConnectionFailure:
        logger.error("Failed to connect to MongoDB")
        raise
    except ServerSelectionTimeoutError:
        logger.error("Could not connect to MongoDB server")
        raise
    except Exception as e:
        logger.error(f"An error occurred while connecting to MongoDB: {e}")
        raise

# Create unique indexes if they don't exist
async def ensure_indexes(database: AsyncIOMotorDatabase) -> None:
    """
    Ensure unique indexes exist for the collections.
    """
    logger.info("Ensuring indexes on the database.")
    if database is None:
        logger.error("Database must be provided.")
        raise ValueError("Database must be provided")
    try:
        logger.info("Creating index on chord_progressions...")
        await database.chord_progressions.create_index("name", unique=True)
        logger.info("Index created for chord_progressions.")
        logger.info(f"Index created for chord_progressions with keys: {await database.chord_progressions.index_information()}")
        logger.info(f"Chord progressions collection stats: {await database.chord_progressions.stats()}")
        logger.info(f"Chord progressions collection index sizes: {await database.chord_progressions.index_sizes()}")
    except Exception as e:
        logger.warning(f"Error creating index on chord_progressions: {e}")
        logger.error(f"Chord progressions collection error: {database.chord_progressions.error}")

    try:
        logger.info("Creating index on note_patterns...")
        await database.note_patterns.create_index("name", unique=True)
        logger.info("Index created for note_patterns.")
        logger.info(f"Index created for note_patterns with keys: {await database.note_patterns.index_information()}")
        logger.info(f"Note patterns collection stats: {await database.note_patterns.stats()}")
        logger.info(f"Note patterns collection index sizes: {await database.note_patterns.index_sizes()}")
    except Exception as e:
        logger.warning(f"Error creating index on note_patterns: {e}")
        logger.error(f"Note patterns collection error: {database.note_patterns.error}")

    try:
        logger.info("Creating index on rhythm_patterns...")
        await database.rhythm_patterns.create_index("name", unique=True)
        logger.info("Index created for rhythm_patterns.")
        logger.info(f"Index created for rhythm_patterns with keys: {await database.rhythm_patterns.index_information()}")
        logger.info(f"Rhythm patterns collection stats: {await database.rhythm_patterns.stats()}")
        logger.info(f"Rhythm patterns collection index sizes: {await database.rhythm_patterns.index_sizes()}")
    except Exception as e:
        logger.warning(f"Error creating index on rhythm_patterns: {e}")
        logger.error(f"Rhythm patterns collection error: {database.rhythm_patterns.error}")

def serialize_rhythm_pattern(pattern: RhythmPatternData) -> Dict[str, Any]:
    return {
        'notes': [
            {
                'position': note.position,
                'duration': note.duration,
                'velocity': note.velocity,
                'is_rest': note.is_rest,
                'accent': note.accent,
                'swing_ratio': note.swing_ratio
            } for note in pattern.notes
        ],
        'time_signature': pattern.time_signature,
        'swing_enabled': pattern.swing_enabled,
        'humanize_amount': pattern.humanize_amount,
        'swing_ratio': pattern.swing_ratio,
        'style': pattern.style,
        'default_duration': pattern.default_duration,
        'total_duration': pattern.total_duration,
        'accent_pattern': pattern.accent_pattern,
        'groove_type': pattern.groove_type,
        'variation_probability': pattern.variation_probability,
        'duration': pattern.duration
    }

# Function to clear existing data
async def clear_existing_data(database: AsyncIOMotorDatabase) -> None:
    logger.info("Clearing existing data from the database.")
    try:
        logger.info("Deleting documents from chord_progressions...")
        result = await database.chord_progressions.delete_many({})
        logger.info(f"Cleared existing data from chord_progressions. Deleted {result.deleted_count} documents.")
        logger.info(f"Chord progressions collection stats after deletion: {await database.chord_progressions.stats()}")
        logger.info(f"Chord progressions collection index sizes after deletion: {await database.chord_progressions.index_sizes()}")
    except Exception as e:
        logger.warning(f"Error clearing existing data from chord_progressions: {e}")
        logger.error(f"Chord progressions collection error: {database.chord_progressions.error}")

    try:
        logger.info("Deleting documents from note_patterns...")
        result = await database.note_patterns.delete_many({})
        logger.info(f"Cleared existing data from note_patterns. Deleted {result.deleted_count} documents.")
        logger.info(f"Note patterns collection stats after deletion: {await database.note_patterns.stats()}")
        logger.info(f"Note patterns collection index sizes after deletion: {await database.note_patterns.index_sizes()}")
    except Exception as e:
        logger.warning(f"Error clearing existing data from note_patterns: {e}")
        logger.error(f"Note patterns collection error: {database.note_patterns.error}")

    try:
        logger.info("Deleting documents from rhythm_patterns...")
        result = await database.rhythm_patterns.delete_many({})
        logger.info(f"Cleared existing data from rhythm_patterns. Deleted {result.deleted_count} documents.")
        logger.info(f"Rhythm patterns collection stats after deletion: {await database.rhythm_patterns.stats()}")
        logger.info(f"Rhythm patterns collection index sizes after deletion: {await database.rhythm_patterns.index_sizes()}")
    except Exception as e:
        logger.warning(f"Error clearing existing data from rhythm_patterns: {e}")
        logger.error(f"Rhythm patterns collection error: {database.rhythm_patterns.error}")

# Function to import chord progressions
async def import_chord_progressions(database: AsyncIOMotorDatabase) -> None:
    logger.info("Importing chord progressions into the database.")
    target_db: AsyncIOMotorDatabase = database
    for i, (name, progression) in enumerate(COMMON_PROGRESSIONS.items(), start=1):
        try:
            logger.info(f"Inserting chord progression: {name}...")
            result = await target_db.chord_progressions.insert_one({
                "name": name,
                "progression": progression,
            })
            logger.info(f"Imported chord progression: {name}. Inserted ID: {result.inserted_id}")
            logger.info(f"Chord progressions collection stats after insertion: {await target_db.chord_progressions.stats()}")
            logger.info(f"Chord progressions collection index sizes after insertion: {await target_db.chord_progressions.index_sizes()}")
        except Exception as e:
            logger.warning(f"Error importing chord progression: {name} - {e}")
            logger.error(f"Chord progressions collection error: {target_db.chord_progressions.error}")

# Function to import note patterns
async def import_note_patterns(database: AsyncIOMotorDatabase) -> None:
    logger.info("Importing note patterns into the database.")
    target_db: AsyncIOMotorDatabase = database
    for i, (name, pattern) in enumerate(NOTE_PATTERNS.items(), start=1):
        try:
            logger.info(f"Inserting note pattern: {name}...")
            result = await target_db.note_patterns.insert_one({
                "name": name,
                "pattern": pattern,
            })
            logger.info(f"Imported note pattern: {name}. Inserted ID: {result.inserted_id}")
            logger.info(f"Note patterns collection stats after insertion: {await target_db.note_patterns.stats()}")
            logger.info(f"Note patterns collection index sizes after insertion: {await target_db.note_patterns.index_sizes()}")
        except Exception as e:
            logger.warning(f"Error importing note pattern: {name} - {e}")
            logger.error(f"Note patterns collection error: {target_db.note_patterns.error}")

# Function to import rhythm patterns
async def import_rhythm_patterns(database: AsyncIOMotorDatabase) -> None:
    logger.info("Importing rhythm patterns into the database.")
    target_db: AsyncIOMotorDatabase = database
    for i, (name, pattern) in enumerate(RHYTHM_PATTERNS.items(), start=1):
        serialized_pattern = serialize_rhythm_pattern(pattern)
        try:
            logger.info(f"Inserting rhythm pattern: {name}...")
            result = await target_db.rhythm_patterns.insert_one({
                "name": name,
                "pattern": serialized_pattern,
            })
            logger.info(f"Imported rhythm pattern: {name}. Inserted ID: {result.inserted_id}")
            logger.info(f"Rhythm patterns collection stats after insertion: {await target_db.rhythm_patterns.stats()}")
            logger.info(f"Rhythm patterns collection index sizes after insertion: {await target_db.rhythm_patterns.index_sizes()}")
        except Exception as e:
            logger.warning(f"Error importing rhythm pattern: {name} - {e}")
            logger.error(f"Rhythm patterns collection error: {target_db.rhythm_patterns.error}")

async def import_presets_if_empty(database: AsyncIOMotorDatabase) -> None:
    """
    Import presets into the database if collections are empty.
    """
    logger.info("Importing presets into the database if collections are empty.")
    await clear_existing_data(database)  # Clear existing data before import

    # Ensure indexes are created before importing data
    await ensure_indexes(database)

    # Check if collections are empty before importing
    if await database.chord_progressions.count_documents({}) == 0:
        await import_chord_progressions(database)

    if await database.note_patterns.count_documents({}) == 0:
        await import_note_patterns(database)

    if await database.rhythm_patterns.count_documents({}) == 0:
        await import_rhythm_patterns(database)

async def run_imports():
    try:
        logger.info("Connecting to MongoDB...")
        client = await initialize_client()
        logger.info("Connected to MongoDB.")
        print("Clearing existing data...")
        await clear_existing_data(client["note_gen"])
        print("Creating indexes...")
        await ensure_indexes(client["note_gen"])
        print("Importing presets...")
        await import_presets_if_empty(client["note_gen"])
        print("Done!")
    except ConnectionFailure:
        logger.error("Failed to connect to MongoDB")
        print("Failed to connect to MongoDB")
    except ServerSelectionTimeoutError:
        logger.error("Could not connect to MongoDB server")
        print("Could not connect to MongoDB server")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

# Main function to run the import
if __name__ == '__main__':
    import asyncio
    asyncio.run(run_imports())
