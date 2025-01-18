"""Module for importing preset data into MongoDB."""

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.database import Database
import logging
import os
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.rhythm_pattern import RhythmPatternData
from typing import Any, Optional, Dict

# MongoDB connection setup
client: MongoClient[str] = MongoClient("mongodb://localhost:27017/")
db: Database = client["note_gen"]

# Create unique indexes if they don't exist
async def ensure_indexes(database: AsyncIOMotorDatabase) -> None:
    if database is None:
        raise ValueError("Database must be provided")
    target_db: AsyncIOMotorDatabase = database
    try:
        await target_db.chord_progressions.create_index("name", unique=True)
    except Exception as e:
        logger.warning(f"Index already exists or error creating index on chord_progressions: {e}")

    try:
        await target_db.note_patterns.create_index("name", unique=True)
    except Exception as e:
        logger.warning(f"Index already exists or error creating index on note_patterns: {e}")

    try:
        await target_db.rhythm_patterns.create_index("name", unique=True)
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
def clear_existing_data() -> None:
    db.chord_progressions.delete_many({})
    db.note_patterns.delete_many({})
    db.rhythm_patterns.delete_many({})

# Function to import chord progressions
def import_chord_progressions(database: Optional[Database] = None) -> None:
    target_db: Database = database if database is not None else db
    for i, (name, progression) in enumerate(COMMON_PROGRESSIONS.items(), start=1):
        target_db.chord_progressions.insert_one({
            'id': str(i),  # Use string for consistency with UUIDs
            'name': name,
            'scale_info': progression['scale_info'],  # Include scale_info
            'chords': progression['chords']  # Include chords
        })

# Function to import note patterns
def import_note_patterns(database: Optional[Database] = None) -> None:
    target_db: Database = database if database is not None else db
    for i, (name, pattern) in enumerate(NOTE_PATTERNS.items(), start=1):
        target_db.note_patterns.insert_one({
            'id': str(i),  # Use string for consistency with UUIDs
            'name': name,
            'data': pattern['data'],  # Include data
            'notes': pattern['notes'],  # Include notes
            'description': pattern.get('description', ''),  # Optional field
            'tags': pattern.get('tags', []),  # Optional field
            'is_test': pattern.get('is_test', False)  # Optional field
        })

# Function to import rhythm patterns
def import_rhythm_patterns(database: Optional[Database] = None) -> None:
    target_db: Database = database if database is not None else db
    for i, (name, pattern) in enumerate(RHYTHM_PATTERNS.items(), start=1):
        serialized_pattern = serialize_rhythm_pattern(pattern)
        target_db.rhythm_patterns.insert_one({
            'id': str(i),  # Use string for consistency with UUIDs
            'name': name,
            'data': serialized_pattern,  # Include serialized pattern data
            'description': pattern.get('description', ''),  # Optional field
            'tags': pattern.get('tags', []),  # Optional field
            'is_test': pattern.get('is_test', False)  # Optional field
        })

async def import_presets_if_empty(database: AsyncIOMotorDatabase) -> None:
    """Import presets if collections are empty and not in test mode."""
    # Skip import if in test mode
    if os.getenv("TESTING"):
        logger.info("Skipping preset import in test mode")
        return

    # Check if collections are empty
    chord_count = await database.chord_progressions.count_documents({})
    note_count = await database.note_patterns.count_documents({})
    rhythm_count = await database.rhythm_patterns.count_documents({})

    if chord_count == 0 and note_count == 0 and rhythm_count == 0:
        logger.info("Collections are empty, importing presets...")
        try:
            # Import presets
            import_chord_progressions()
            import_note_patterns()
            import_rhythm_patterns()
            logger.info("Successfully imported presets")
        except Exception as e:
            logger.error(f"Error importing presets: {e}")
    else:
        logger.info("Collections already contain data, skipping preset import")

# Main function to run the import
if __name__ == '__main__':
    try:
        print("Clearing existing data...")
        clear_existing_data()
        print("Creating indexes...")
        ensure_indexes(AsyncIOMotorDatabase(client, "note_gen"))
        print("Importing presets...")
        import_presets_if_empty(AsyncIOMotorDatabase(client, "note_gen"))        
        print("Done!")
    except ConnectionFailure:
        print("Failed to connect to MongoDB")
    except ServerSelectionTimeoutError:
        print("Could not connect to MongoDB server")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
