from pymongo import MongoClient
from bson import ObjectId
import uuid

# Import the actual presets
from src.note_gen.models.presets import (
    COMMON_PROGRESSIONS,
    NOTE_PATTERNS,
    RHYTHM_PATTERNS,
    DEFAULT_KEY,
    DEFAULT_SCALE_TYPE
)
from src.note_gen.models.rhythm_pattern import RhythmPatternData

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['note_gen']

# Clear existing data
db.chord_progressions.delete_many({})
db.note_patterns.delete_many({})
db.rhythm_patterns.delete_many({})

def format_chord_progression(name: str, progression: list) -> dict:
    """Format a chord progression according to the model requirements."""
    def convert_roman_to_note(roman: str, key: str = "C") -> dict:
        # Strip any quality indicators from the roman numeral
        base_roman = ''.join(c for c in roman if c.isalpha())
        quality = ''.join(c for c in roman if not c.isalpha())
        
        # Map roman numerals to scale degrees
        roman_to_degree = {
            'I': 0, 'II': 2, 'III': 4, 'IV': 5, 'V': 7, 'VI': 9, 'VII': 11,
            'i': 0, 'ii': 2, 'iii': 4, 'iv': 5, 'v': 7, 'vi': 9, 'vii': 11
        }
        
        # Map scale degree to note name
        major_scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        degree = roman_to_degree.get(base_roman.upper(), 0)
        note_name = major_scale[degree % 7]
        
        # Determine quality based on roman numeral case and any modifiers
        if quality:
            chord_quality = quality
        else:
            chord_quality = 'MINOR' if base_roman.islower() else 'MAJOR'
            
        if '°' in roman or 'dim' in roman:
            chord_quality = 'DIMINISHED'
        elif 'aug' in roman:
            chord_quality = 'AUGMENTED'
        
        return {
            'root': {'note_name': note_name, 'octave': 4},
            'quality': chord_quality
        }

    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'scale_info': {
            'root': {'note_name': DEFAULT_KEY, 'octave': 4},
            'scale_type': DEFAULT_SCALE_TYPE
        },
        'chords': [
            convert_roman_to_note(chord) if any(c.isalpha() for c in chord) else 
            {'root': {'note_name': chord[0], 'octave': 4}, 
             'quality': chord[1:] if len(chord) > 1 else 'MAJOR'} 
            for chord in progression
        ],
        'key': DEFAULT_KEY,
        'scale_type': DEFAULT_SCALE_TYPE,
        'description': f'Progression: {name}',
        'tags': ['preset'],
        'complexity': 1.0,
        'is_test': False
    }

def format_note_pattern(name: str, pattern: list) -> dict:
    """Format a note pattern according to the model requirements."""
    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'data': pattern,
        'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0} for _ in pattern],
        'description': f'Pattern: {name}',
        'tags': ['preset'],
        'is_test': False
    }

def format_rhythm_pattern(name: str, pattern: 'RhythmPatternData') -> dict:
    """Format a rhythm pattern according to the model requirements."""
    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'data': {
            'notes': [{
                'position': note.position,
                'duration': note.duration,
                'velocity': note.velocity,
                'is_rest': note.is_rest,
                'accent': note.accent,
                'swing_ratio': note.swing_ratio
            } for note in pattern.notes],
            'time_signature': pattern.time_signature,
            'swing_enabled': pattern.swing_enabled,
            'humanize_amount': pattern.humanize_amount,
            'swing_ratio': pattern.swing_ratio,
            'default_duration': pattern.default_duration,
            'total_duration': pattern.total_duration,
            'accent_pattern': pattern.accent_pattern,
            'groove_type': pattern.groove_type,
            'variation_probability': pattern.variation_probability,
            'duration': pattern.duration,
            'style': pattern.style
        },
        'description': f'Rhythm: {name}',
        'tags': ['preset'],
        'complexity': 1.0,
        'style': pattern.style,
        'is_test': False
    }

# Format and prepare all progressions
chord_progressions = [
    format_chord_progression(name, prog)
    for name, prog in COMMON_PROGRESSIONS.items()
]

# Format and prepare all note patterns
note_patterns = [
    format_note_pattern(name, pattern)
    for name, pattern in NOTE_PATTERNS.items()
]

# Format and prepare all rhythm patterns
rhythm_patterns = [
    format_rhythm_pattern(name, pattern)
    for name, pattern in RHYTHM_PATTERNS.items()
]

# Insert the data
try:
    if chord_progressions:
        result = db.chord_progressions.insert_many(chord_progressions)
        print(f"Inserted {len(result.inserted_ids)} chord progressions")
    
    if note_patterns:
        result = db.note_patterns.insert_many(note_patterns)
        print(f"Inserted {len(result.inserted_ids)} note patterns")
    
    if rhythm_patterns:
        result = db.rhythm_patterns.insert_many(rhythm_patterns)
        print(f"Inserted {len(result.inserted_ids)} rhythm patterns")
        
    print("Database population completed successfully")
    
except Exception as e:
    print(f"Error populating database: {str(e)}")
