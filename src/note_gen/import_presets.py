import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

from src.note_gen.models.presets import DEFAULT_CHORD_PROGRESSION, DEFAULT_NOTE_PATTERN, COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData
from typing import List, Any, Optional, Dict


# MongoDB connection setup
client: pymongo.MongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["note_gen"]

# Create unique indexes if they don't exist
def ensure_indexes(database=None):
    target_db = database if database is not None else db
    try:
        target_db.chord_progressions.create_index("name", unique=True)
    except Exception as e:
        logger.warning(f"Index already exists or error creating index on chord_progressions: {e}")

    try:
        target_db.note_patterns.create_index("name", unique=True)
    except Exception as e:
        logger.warning(f"Index already exists or error creating index on note_patterns: {e}")

    try:
        target_db.rhythm_patterns.create_index("name", unique=True)
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
def import_chord_progressions(database=None) -> None:
    target_db = database if database is not None else db
    for i, (name, progression) in enumerate(COMMON_PROGRESSIONS.items(), start=1):
        target_db.chord_progressions.insert_one({
            'id': i,
            'name': name,
            'progression': progression
        })

# Function to import note patterns
def import_note_patterns(database=None) -> None:
    target_db = database if database is not None else db
    for i, (name, pattern) in enumerate(NOTE_PATTERNS.items(), start=1):
        target_db.note_patterns.insert_one({
            'id': i,
            'name': name,
            'pattern': pattern
        })

# Function to import rhythm patterns
def import_rhythm_patterns(database=None) -> None:
    target_db = database if database is not None else db
    for i, (name, pattern) in enumerate(RHYTHM_PATTERNS.items(), start=1):
        serialized_pattern = serialize_rhythm_pattern(pattern)
        target_db.rhythm_patterns.insert_one({
            'id': i,
            'name': name,
            'pattern': serialized_pattern
        })

async def import_presets_if_empty(database=None):
    """Import presets if collections are empty."""
    target_db = database if database is not None else db
    try:
        if target_db.chord_progressions.count_documents({}) == 0:
            import_chord_progressions(target_db)
            logger.info("Imported chord progressions")
            
        if target_db.note_patterns.count_documents({}) == 0:
            import_note_patterns(target_db)
            logger.info("Imported note patterns")
            
        if target_db.rhythm_patterns.count_documents({}) == 0:
            import_rhythm_patterns(target_db)
            logger.info("Imported rhythm patterns")
    except Exception as e:
        logger.error(f"Error checking/importing presets: {e}")

# Main function to run the import
if __name__ == '__main__':
    try:
        print("Clearing existing data...")
        clear_existing_data()
        
        print("Creating indexes...")
        ensure_indexes()
        
        print("Importing chord progressions...")
        import_chord_progressions()
        
        print("Importing note patterns...")
        import_note_patterns()
        
        print("Importing rhythm patterns...")
        import_rhythm_patterns()
        
        print("Import completed successfully!")
    except (ConnectionFailure, ServerSelectionTimeoutError):
        print("Error: Could not connect to MongoDB. Make sure MongoDB is running.")
    except Exception as e:
        print(f"An error occurred during import: {str(e)}")
