from pymongo import MongoClient
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_note(note: Dict[str, Any]) -> bool:
    """Validate a note object."""
    valid_note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    if not isinstance(note.get('octave'), int) or not (0 <= note['octave'] <= 8):
        return False
    if note.get('note_name') not in valid_note_names:
        return False
    if not isinstance(note.get('duration'), (int, float)) or note['duration'] <= 0:
        return False
    return True

def validate_rhythm_note(note: Dict[str, Any]) -> bool:
    """Validate a rhythm note object."""
    if not isinstance(note.get('position'), (int, float)) or note['position'] < 0:
        return False
    if not isinstance(note.get('duration'), (int, float)) or note['duration'] <= 0:
        return False
    if not isinstance(note.get('velocity'), int) or not (0 <= note['velocity'] <= 127):
        return False
    return True

def validate_note_pattern(pattern: Dict[str, Any]) -> bool:
    """Validate a note pattern."""
    # Skip test patterns
    if pattern.get('name', '').startswith('Test '):
        return True
        
    if not pattern.get('notes') or not isinstance(pattern['notes'], list):
        return False
    if not all(validate_note(note) for note in pattern['notes']):
        return False
    if pattern.get('pattern_type') not in ['melodic', 'harmonic', 'rhythmic']:
        return False
    if not isinstance(pattern.get('complexity'), (int, float)) or not (0 <= pattern['complexity'] <= 1):
        return False
    return True

def validate_rhythm_pattern(pattern: Dict[str, Any]) -> bool:
    """Validate a rhythm pattern."""
    # Skip test patterns
    if pattern.get('name', '').startswith('Test '):
        return True
        
    data = pattern.get('data', {})
    if not data.get('notes') or not isinstance(data['notes'], list):
        return False
    if not all(validate_rhythm_note(note) for note in data['notes']):
        return False
    if not isinstance(data.get('humanize_amount'), (int, float)) or not (0 <= data['humanize_amount'] <= 1):
        return False
    if not isinstance(data.get('swing_ratio'), (int, float)) or not (0.5 <= data['swing_ratio'] <= 0.75):
        return False
    if not isinstance(data.get('variation_probability'), (int, float)) or not (0 <= data['variation_probability'] <= 1):
        return False
    if data.get('style') not in ['basic', 'jazz', 'rock', 'latin', 'funk']:
        return False
    if data.get('groove_type') not in ['straight', 'swing', 'shuffle', 'latin']:
        return False
    return True

def validate_chord_progression(progression: Dict[str, Any]) -> bool:
    """Validate a chord progression."""
    # Skip test patterns
    if progression.get('name', '').startswith('Test '):
        return True
        
    valid_keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    valid_scale_types = ['major', 'minor', 'harmonic_minor', 'melodic_minor']
    
    if not progression.get('chords') or not isinstance(progression['chords'], list):
        return False
    if progression.get('key') not in valid_keys:
        return False
    if progression.get('scale_type') not in valid_scale_types:
        return False
    if not isinstance(progression.get('complexity'), (int, float)) or not (0 <= progression['complexity'] <= 1):
        return False
    return True

def cleanup_database():
    """Clean up invalid patterns in the database."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client.note_gen
    
    try:
        # Remove patterns without IDs
        result = db.note_patterns.delete_many({"id": {"$exists": False}})
        logger.info(f"Removed {result.deleted_count} note patterns without IDs")

        result = db.rhythm_patterns.delete_many({"id": {"$exists": False}})
        logger.info(f"Removed {result.deleted_count} rhythm patterns without IDs")

        # Clean up note patterns
        note_patterns = list(db.note_patterns.find({}))
        for pattern in note_patterns:
            if not validate_note_pattern(pattern):
                db.note_patterns.delete_one({'_id': pattern['_id']})
                logger.info(f"Deleted invalid note pattern: {pattern.get('name', 'unnamed')}")
        
        # Clean up rhythm patterns
        rhythm_patterns = list(db.rhythm_patterns.find({}))
        for pattern in rhythm_patterns:
            if not validate_rhythm_pattern(pattern):
                db.rhythm_patterns.delete_one({'_id': pattern['_id']})
                logger.info(f"Deleted invalid rhythm pattern: {pattern.get('name', 'unnamed')}")
        
        # Clean up chord progressions
        chord_progressions = list(db.chord_progressions.find({}))
        for progression in chord_progressions:
            if not validate_chord_progression(progression):
                db.chord_progressions.delete_one({'_id': progression['_id']})
                logger.info(f"Deleted invalid chord progression: {progression.get('name', 'unnamed')}")
        
        logger.info("Database cleanup completed successfully")
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    cleanup_database()
