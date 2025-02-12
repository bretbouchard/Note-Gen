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
            default_progressions = [
                {"name": "Default Progression 1", "chords": [], "key": "C", "scale_type": "MAJOR"},
                {"name": "Default Progression 2", "chords": [], "key": "G", "scale_type": "MAJOR"},
            ]
            await db.chord_progressions.insert_many(default_progressions)

        # Check if note_patterns collection is empty
        if not await db.note_patterns.count_documents({}):
            # Insert default note patterns
            default_patterns = [
                {"name": "Simple Triad", "pattern": {"index": 1, "pattern": [0, 2, 4], "tags": ["triad", "basic"], "complexity": 0.5, "description": "A simple triad pattern."}, "complexity": 1, "pattern_type": "default_type"},
                {"name": "Ascending Scale", "pattern": {"index": 2, "pattern": [0, 1, 2, 3, 4, 5, 6, 7], "tags": ["scale", "ascending"], "complexity": 0.3, "description": "An ascending scale pattern."}, "complexity": 1, "pattern_type": "default_type"},
                {"name": "Descending Scale", "pattern": {"index": 3, "pattern": [7, 6, 5, 4, 3, 2, 1, 0], "tags": ["scale", "descending"], "complexity": 0.3, "description": "A descending scale pattern."}, "complexity": 1, "pattern_type": "default_type"},
                {"name": "Arpeggio", "pattern": {"index": 4, "pattern": [0, 2, 4, 7], "tags": ["arpeggio", "broken chord"], "complexity": 0.4, "description": "An arpeggio pattern."}, "complexity": 1, "pattern_type": "default_type"},
                {"name": "Pentatonic", "pattern": {"index": 5, "pattern": [0, 2, 4, 7, 9], "tags": ["pentatonic", "scale"], "complexity": 0.4, "description": "A pentatonic scale pattern."}, "complexity": 1, "pattern_type": "default_type"},
            ]
            for pattern in default_patterns:
                existing_pattern = await db.note_patterns.find_one({"pattern.index": pattern["pattern"]["index"]})
                if existing_pattern:
                    logger.warning(f"Pattern with index '{pattern['pattern']['index']}' already exists. Skipping insertion.")
                else:
                    await db.note_patterns.insert_one(pattern)

        # Check if rhythm_patterns collection is empty
        if not await db.rhythm_patterns.count_documents({}):
            # Insert default rhythm patterns
            default_rhythms = [
                {"complexity": 0.5, "pattern": []},
                {"complexity": 0.75, "pattern": []},
            ]
            await db.rhythm_patterns.insert_many(default_rhythms)

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
            
            # Create a ChordProgression instance
            chord_progression = ChordProgression(
                name=name,
                chords=[],  # You might want to generate chords based on progression
                key="C",  # Default key
                scale_type="MAJOR",
                complexity=0.5,  # Default complexity
                scale_info=ScaleInfo(root=Note('C'), scale_type=ScaleType.MAJOR)
            )
            
            # Convert to dictionary for database storage
            progression_data = chord_progression.to_dict()
            
            # Add additional metadata
            progression_data.update({
                "style": "default",
                "description": f"Standard {name} progression",
                "difficulty": "intermediate",
                "tags": [name.lower().replace(" ", "-")],
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow()
            })
            
            result = await target_db.chord_progressions.insert_one(progression_data)
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
    for i, (name, pattern_dict) in enumerate(RHYTHM_PATTERNS.items(), start=1):
        logger.info(f"Processing pattern: {name}, Data: {pattern_dict}")  # Log the pattern data
        
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
            logger.info(f"Inserting rhythm pattern: {name}...")
            result = await target_db.rhythm_patterns.insert_one({
                "name": name,
                "pattern": serialized_pattern,
            })
            logger.info(f"Imported rhythm pattern: {name}. Inserted ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"Error inserting rhythm pattern {name}: {e}")

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
