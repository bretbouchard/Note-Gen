import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from src.note_gen.models.presets import DEFAULT_CHORD_PROGRESSION, DEFAULT_NOTE_PATTERN, COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData
from typing import List, Any, Optional, Dict


# MongoDB connection setup
client: pymongo.MongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["note_gen"]

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
def import_chord_progressions() -> None:
    for i, (name, progression) in enumerate(COMMON_PROGRESSIONS.items(), start=1):
        db.chord_progressions.insert_one({
            'id': i,
            'name': name,
            'progression': progression
        })

# Function to import note patterns
def import_note_patterns() -> None:
    for i, (name, pattern) in enumerate(NOTE_PATTERNS.items(), start=1):
        db.note_patterns.insert_one({
            'id': i,
            'name': name,
            'pattern': pattern
        })

# Function to import rhythm patterns
def import_rhythm_patterns() -> None:
    for i, (name, pattern) in enumerate(RHYTHM_PATTERNS.items(), start=1):
        serialized_pattern = serialize_rhythm_pattern(pattern)
        db.rhythm_patterns.insert_one({
            'id': i,
            'name': name,
            'pattern': serialized_pattern
        })

# Main function to run the import
if __name__ == '__main__':
    try:
        print("Clearing existing data...")
        clear_existing_data()
        
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
