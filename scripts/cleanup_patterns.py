# scripts/cleanup_patterns.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any
import asyncio


# [Note and RhythmNote classes remain unchanged]
class Note:
    def __init__(self, octave: int, note_name: str, duration: float):
        self.octave = octave
        self.note_name = note_name
        self.duration = duration

class RhythmNote:
    def __init__(self, position: float, duration: float, velocity: int):
        self.position = position
        self.duration = duration
        self.velocity = velocity

# [All validation functions remain unchanged]
def validate_note(note: Note) -> bool:
    """Validate a note object."""
    valid_note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    if not isinstance(note.octave, int) or not (0 <= note.octave <= 8):
        return False
    if note.note_name not in valid_note_names:
        return False
    if not isinstance(note.duration, (int, float)) or note.duration <= 0:
        return False
    return True

def validate_rhythm_note(note: Note) -> bool:
    """Validate a rhythm note object."""
    if not isinstance(note.position, (int, float)) or note.position < 0:
        return False
    if not isinstance(note.duration, (int, float)) or note.duration <= 0:
        return False
    if not isinstance(note.velocity, int) or not (0 <= note.velocity <= 127):
        return False
    return True

def validate_note_pattern(pattern: Dict[str, Any]) -> bool:
    """Validate a note pattern."""
    if pattern.get('name', '').startswith('Test '):
        return True
        
    if not pattern.get('notes') or not isinstance(pattern['notes'], list):
        return False
    if not all(validate_note(Note(**note)) for note in pattern['notes']):
        return False
    if pattern.get('pattern_type') not in ['melodic', 'harmonic', 'rhythmic']:
        return False
    if not isinstance(pattern.get('complexity'), (int, float)) or not (0 <= pattern['complexity'] <= 1):
        return False
    return True

def validate_rhythm_pattern(pattern: Dict[str, Any]) -> bool:
    """Validate a rhythm pattern."""
    if pattern.get('name', '').startswith('Test '):
        return True
        
    data = pattern.get('data', {})
    if not data.get('notes') or not isinstance(data['notes'], list):
        return False
    if not all(validate_rhythm_note(RhythmNote(**note)) for note in data['notes']):
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
    if progression.get('name', '').startswith('Test '):
        return True
        
    valid_keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    valid_scale_types = ['MAJOR', 'MINOR', 'HARMONIC_MINOR', 'MELODIC_MINOR']
    
    if not progression.get('chords') or not isinstance(progression['chords'], list):
        return False
    if progression.get('key') not in valid_keys:
        return False
    if progression.get('scale_type') not in valid_scale_types:
        return False
    if not isinstance(progression.get('complexity'), (int, float)) or not (0 <= progression['complexity'] <= 1):
        return False
    return True

async def cleanup_database() -> None:
    """Clean up invalid patterns in the database using async operations."""
    client = AsyncIOMotorClient('mongodb://localhost:27017/')
    db = client.note_gen
    
    try:
        # Remove patterns without IDs
        result = await db.note_patterns.delete_many({"id": {"$exists": False}})
        print(f"Removed {result.deleted_count} note patterns without IDs")

        result = await db.rhythm_patterns.delete_many({"id": {"$exists": False}})
        print(f"Removed {result.deleted_count} rhythm patterns without IDs")

        # Clean up note patterns
        async for pattern in db.note_patterns.find({}):
            if not validate_note_pattern(pattern):
                await db.note_patterns.delete_one({'_id': pattern['_id']})
                print(f"Deleted invalid note pattern: {pattern.get('name', 'unnamed')}")
        
        # Clean up rhythm patterns
        async for pattern in db.rhythm_patterns.find({}):
            if not validate_rhythm_pattern(pattern):
                await db.rhythm_patterns.delete_one({'_id': pattern['_id']})
                print(f"Deleted invalid rhythm pattern: {pattern.get('name', 'unnamed')}")
        
        # Clean up chord progressions
        async for progression in db.chord_progressions.find({}):
            if not validate_chord_progression(progression):
                await db.chord_progressions.delete_one({'_id': progression['_id']})
                print(f"Deleted invalid chord progression: {progression.get('name', 'unnamed')}")
        
        print("Database cleanup completed successfully")
    
    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_database())