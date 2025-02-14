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
from src.note_gen.models.chord_progression import ChordProgression, ScaleInfo, Note, ScaleType
from typing import Any, Optional, Dict


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
async def import_chord_progressions(db: AsyncIOMotorDatabase) -> None:
    """Import chord progressions from COMMON_PROGRESSIONS into the database."""
    logger.info("Importing chord progressions...")
    for name, chords in COMMON_PROGRESSIONS.items():
        try:
            # Insert each chord progression into the database
            data = {
                'name': name,
                'chords': chords,
                'key': 'C',  # Default key, can be adjusted
                'scale_type': 'MAJOR',  # Default scale type, can be adjusted
                'tags': [],  # Add tags if needed
                'complexity': 0.5,  # Default complexity
                'description': f"{name} progression"
            }
            await db.chord_progressions.insert_one(data)
            logger.info(f"Inserted chord progression: {name}")
        except Exception as e:
            logger.warning(f"Error importing chord progression: {name} - {e}")
    logger.info("Finished importing chord progressions.")

# Function to import note patterns
async def import_note_patterns(database: AsyncIOMotorDatabase) -> None:
    logger.info("Importing note patterns into the database.")
    target_db: AsyncIOMotorDatabase = database
    for i, (name, pattern) in enumerate(NOTE_PATTERNS.items(), start=1):
        try:
            result = await target_db.note_patterns.insert_one({
                "name": name,
                "pattern": pattern,
            })
            logger.info(f"Imported note pattern: {name}. Inserted ID: {result.inserted_id}")
        except Exception as e:
            logger.warning(f"Error importing note pattern: {name} - {e}")
    logger.info("Finished importing note patterns.")

# Function to import rhythm patterns
async def import_rhythm_patterns(database: AsyncIOMotorDatabase) -> None:
    logger.info("Importing rhythm patterns into the database.")
    target_db: AsyncIOMotorDatabase = database
    for i, (name, pattern_dict) in enumerate(RHYTHM_PATTERNS.items(), start=1):
        # Ensure that the notes field is included in the pattern_dict
        notes = pattern_dict.get("notes", [])
        
        # Convert dictionary to RhythmPatternData instance
        pattern = RhythmPatternData(
            index=pattern_dict["index"],
            pattern=pattern_dict["pattern"],
            notes=notes,  # Ensure notes are included
            tags=pattern_dict["tags"],
            complexity=pattern_dict["complexity"],
            description=pattern_dict["description"]
        )
        
        serialized_pattern = serialize_rhythm_pattern(pattern)
        try:
            result = await target_db.rhythm_patterns.insert_one({
                "name": name,
                "pattern": serialized_pattern,
            })
            logger.info(f"Imported rhythm pattern: {name}. Inserted ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Error inserting rhythm pattern {name}: {e}")
    logger.info("Finished importing rhythm patterns.")

def serialize_rhythm_pattern(pattern: RhythmPatternData) -> Dict[str, Any]:
    if not isinstance(pattern, RhythmPatternData):
        raise ValueError("Expected an instance of RhythmPatternData.")
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
