"""Module for importing preset data into MongoDB."""

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.database import Database
import logging
import os
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.rhythm_pattern import RhythmPatternData
from typing import Any, Optional, Dict

# MongoDB connection setup
client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://localhost:27017/")

# Create unique indexes if they don't exist
async def ensure_indexes(database: AsyncIOMotorDatabase) -> None:
    """
    Ensure unique indexes exist for the collections.
    """
    if database is None:
        raise ValueError("Database must be provided")
    try:
        await database.chord_progressions.create_index("name", unique=True)
    except Exception as e:
        logger.warning(f"Index already exists or error creating index on chord_progressions: {e}")

    try:
        await database.note_patterns.create_index("name", unique=True)
    except Exception as e:
        logger.warning(f"Index already exists or error creating index on note_patterns: {e}")

    try:
        await database.rhythm_patterns.create_index("name", unique=True)
    except Exception as e:
        logger.warning(f"Index already exists or error creating index on rhythm_patterns: {e}")

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
    await database.chord_progressions.delete_many({})
    await database.note_patterns.delete_many({})
    await database.rhythm_patterns.delete_many({})

# Function to import chord progressions
async def import_chord_progressions(database: AsyncIOMotorDatabase) -> None:
    target_db: AsyncIOMotorDatabase = database
    for i, (name, progression) in enumerate(COMMON_PROGRESSIONS.items(), start=1):
        await target_db.chord_progressions.insert_one({
            "name": name,
            "progression": progression,
        })

# Function to import note patterns
async def import_note_patterns(database: AsyncIOMotorDatabase) -> None:
    target_db: AsyncIOMotorDatabase = database
    for i, (name, pattern) in enumerate(NOTE_PATTERNS.items(), start=1):
        await target_db.note_patterns.insert_one({
            "name": name,
            "pattern": pattern,
        })

# Function to import rhythm patterns
async def import_rhythm_patterns(database: AsyncIOMotorDatabase) -> None:
    target_db: AsyncIOMotorDatabase = database
    for i, (name, pattern) in enumerate(RHYTHM_PATTERNS.items(), start=1):
        serialized_pattern = serialize_rhythm_pattern(pattern)
        await target_db.rhythm_patterns.insert_one({
            "name": name,
            "pattern": serialized_pattern,
        })

async def import_presets_if_empty(database: AsyncIOMotorDatabase) -> None:
    """
    Import presets into the database if collections are empty.
    """
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
        print("Clearing existing data...")
        await clear_existing_data(client["note_gen"])
        print("Creating indexes...")
        await ensure_indexes(client["note_gen"])
        print("Importing presets...")
        await import_presets_if_empty(client["note_gen"])
        print("Done!")
    except ConnectionFailure:
        print("Failed to connect to MongoDB")
    except ServerSelectionTimeoutError:
        print("Could not connect to MongoDB server")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to run the import
if __name__ == '__main__':
    import asyncio
    asyncio.run(run_imports())
