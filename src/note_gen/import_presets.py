"""Module for importing preset data into MongoDB."""

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.database import Database
from pymongo import IndexModel
import logging
import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.note_gen.database.db import get_db_conn

logger = logging.getLogger(__name__)

from src.note_gen.models.note import Note
from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.patterns import RhythmPatternData
from src.note_gen.models.scale_info import ScaleInfo 
from src.note_gen.core.enums import ScaleType
from src.note_gen.models.patterns import NotePattern , ChordProgression
from typing import Any, Optional, Dict

# Import Presets Script
# This script is responsible for importing default presets into the MongoDB database.
# It checks if the collections are empty and populates them with predefined data.
# The connection to the MongoDB is established using the AsyncIOMotorClient.
# The database used is 'note_gen'.
# If the TESTING environment variable is set, it clears existing data before importing.

# Function to import presets if collections are empty
async def import_presets_if_empty(db: AsyncIOMotorDatabase) -> None:
    """Import default presets into the database if collections are empty."""
    try:
        # Check if chord_progressions collection is empty
        if not await db.chord_progressions.count_documents({}):
            # Insert default chord progressions
            await import_chord_progressions(db)

        # Check if note_patterns collection is empty
        if not await db.note_patterns.count_documents({}):
            # Insert default note patterns
            await import_note_patterns(db)

        # Check if rhythm_patterns collection is empty
        if not await db.rhythm_patterns.count_documents({}):
            # Insert default rhythm patterns
            await import_rhythm_patterns(db)

    except Exception as e:
        logger.error(f"Error importing presets: {e}")

    # Clear existing data if in testing mode
    if os.getenv('TESTING') == '1':
        # await clear_existing_data(db)
        await ensure_indexes(db)
    else:
        # If not in testing mode, ensure indexes
        await ensure_indexes(db)


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Ensure necessary indexes are created for the collections in the database."""
    try:
        # Chord Progressions Indexes
        await db.chord_progressions.create_indexes([
            IndexModel([('name', 1)], unique=True),  # Unique index on name
            IndexModel([('key', 1)]),  # Index on key for faster filtering
            IndexModel([('scale_type', 1)]),  # Index on scale type
            IndexModel([('complexity', 1)]),  # Index on complexity for range queries
            IndexModel([('tags', 1)]),  # Index on tags for searching
            IndexModel([('created_at', -1)]),  # Index for sorting by creation date
            IndexModel([('difficulty', 1)]),  # Index on difficulty
        ])

        # Note Patterns Indexes
        await db.note_patterns.create_indexes([
            IndexModel([('pattern.index', 1)], unique=True),  # Unique index on pattern.index
            IndexModel([('pattern.tags', 1)]),  # Index on tags for easier searching
            IndexModel([('pattern.complexity', 1)]),  # Index on complexity
        ])

        # Rhythm Patterns Indexes
        await db.rhythm_patterns.create_indexes([
            IndexModel([('complexity', 1)]),  # Index on complexity for faster queries
            IndexModel([('pattern.tags', 1)]),  # Index on tags for easier searching
        ])

        logger.info("Indexes created successfully for all collections.")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


# MongoDB connection setup
async def initialize_client():
    try:
        client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://localhost:27017/")
        logger.info("MongoDB client initialized.")
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

# Function to clear existing data
async def clear_existing_data(database: AsyncIOMotorDatabase) -> None:
    logger.info("Clearing existing data from the database.")
    try:
        logger.info("Deleting documents from chord_progressions...")
        result = await database.chord_progressions.delete_many({})
        logger.info(f"Cleared existing data from chord_progressions. Deleted {result.deleted_count} documents.")
    except Exception as e:
        logger.warning(f"Error clearing existing data from chord_progressions: {e}")

    try:
        logger.info("Deleting documents from note_patterns...")
        result = await database.note_patterns.delete_many({})
        logger.info(f"Cleared existing data from note_patterns. Deleted {result.deleted_count} documents.")
    except Exception as e:
        logger.warning(f"Error clearing existing data from note_patterns: {e}")

    try:
        logger.info("Deleting documents from rhythm_patterns...")
        result = await database.rhythm_patterns.delete_many({})
        logger.info(f"Cleared existing data from rhythm_patterns. Deleted {result.deleted_count} documents.")
    except Exception as e:
        logger.warning(f"Error clearing existing data from rhythm_patterns: {e}")

# Function to import chord progressions
async def import_chord_progressions(db):
    chord_progressions = COMMON_PROGRESSIONS
    await db.chord_progressions.insert_many([
        {
            "name": name,
            "index": data["index"],
            "chords": data["chords"],
            "key": data["key"],
            "scale_type": data["scale_type"],
            "tags": data["tags"],
            "complexity": data["complexity"],
            "description": data["description"]
        }
        for name, data in chord_progressions.items()
    ])

# Function to import note patterns
async def import_note_patterns(db):
    note_patterns = NOTE_PATTERNS
    await db.note_patterns.insert_many([
        {
            "name": name,
            "index": data["index"],
            "pattern": data["pattern"],
            "tags": data["tags"],
            "complexity": data["complexity"],
            "description": data["description"]
        }
        for name, data in note_patterns.items()
    ])

# Function to import rhythm patterns
async def import_rhythm_patterns(db):
    rhythm_patterns = RHYTHM_PATTERNS
    await db.rhythm_patterns.insert_many([
        {
            "name": name,
            "index": data["index"],
            "pattern": data["pattern"],
            "tags": data["tags"],
            "complexity": data["complexity"],
            "description": data["description"],
            "notes": data["notes"]
        }
        for name, data in rhythm_patterns.items()
    ])

async def import_presets():
    db = await get_db_conn()
    await import_chord_progressions(db)
    await import_note_patterns(db)
    await import_rhythm_patterns(db)

# Main function to run the import
async def run_imports():
    await import_presets()

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_imports())
