"""Module for importing preset data into MongoDB."""

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.database import Database
from pymongo import IndexModel
import logging
import os
import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.rhythm_pattern import RhythmPatternData
from typing import Any, Optional, Dict


async def import_presets_if_empty(db: AsyncIOMotorDatabase) -> None:
    """Import default presets into the database if collections are empty."""
    try:
        # Check if chord_progressions collection is empty
        if not await db.chord_progressions.count_documents({}):
            # Insert default chord progressions
            default_progressions = [
                {"name": "Default Progression 1", "chords": [], "key": "C", "scale_type": "major"},
                {"name": "Default Progression 2", "chords": [], "key": "G", "scale_type": "major"},
            ]
            await db.chord_progressions.insert_many(default_progressions)

        # Check if note_patterns collection is empty
        if not await db.note_patterns.count_documents({}):
            # Insert default note patterns
            default_patterns = [
                {"pattern_type": "Basic", "notes": []},
                {"pattern_type": "Advanced", "notes": []},
            ]
            await db.note_patterns.insert_many(default_patterns)

        # Check if rhythm_patterns collection is empty
        if not await db.rhythm_patterns.count_documents({}):
            # Insert default rhythm patterns
            default_rhythms = [
                {"complexity": 0.5, "pattern": []},
                {"complexity": 0.75, "pattern": []},
            ]
            await db.rhythm_patterns.insert_many(default_rhythms)

    except Exception as e:
        print(f"Error importing presets: {e}")


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Ensure necessary indexes are created for the collections in the database."""
    try:
        await db.chord_progressions.create_indexes([
            IndexModel([('name', 1)], unique=True),  # Unique index on name
        ])
        await db.note_patterns.create_indexes([
            IndexModel([('pattern_type', 1)], unique=True),  # Unique index on pattern_type
        ])
        await db.rhythm_patterns.create_indexes([
            IndexModel([('complexity', 1)])  # Index on complexity for faster queries
        ])
    except Exception as e:
        print(f"Error creating indexes: {e}")


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
async def import_chord_progressions(database: AsyncIOMotorDatabase) -> None:
    logger.info("Importing chord progressions into the database.")
    target_db: AsyncIOMotorDatabase = database
    for i, (name, progression) in enumerate(COMMON_PROGRESSIONS.items(), start=1):
        try:
            logger.info(f"Inserting chord progression: {name}...")
            # Add all required fields here
            result = await target_db.chord_progressions.insert_one({
                "name": name,
                "progression": progression,
                "key": "C",  # Default key
                "style": "default",  # Default style
                "description": f"Standard {name} progression",
                "difficulty": "intermediate",
                "tags": [name.lower().replace(" ", "-")],
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow()
            })
            logger.info(f"Imported chord progression: {name}. Inserted ID: {result.inserted_id}")
        except Exception as e:
            logger.warning(f"Error importing chord progression: {name} - {e}")

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
        except Exception as e:
            logger.warning(f"Error importing note pattern: {name} - {e}")

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
        except Exception as e:
            logger.warning(f"Error importing rhythm pattern: {name} - {e}")

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

# Main function to run the import
async def run_imports():
    client = await initialize_client()
    database = client.note_gen
    await clear_existing_data(database)  # Clear existing data before importing
    await import_chord_progressions(database)  # Import chord progressions
    await import_note_patterns(database)  # Import note patterns
    await import_rhythm_patterns(database)  # Import rhythm patterns

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_imports())
