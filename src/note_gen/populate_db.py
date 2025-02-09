from motor import motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from typing import List, Dict, Any
from src.note_gen.models.presets import (
    COMMON_PROGRESSIONS,
    NOTE_PATTERNS,
    RHYTHM_PATTERNS,
    DEFAULT_KEY,
    DEFAULT_SCALE_TYPE
)
from src.note_gen.models.rhythm_pattern import RhythmPatternData
from src.note_gen.models.roman_numeral import RomanNumeral, ChordQualityType

# Import the actual presets


async def clear_existing_data(db: motor_asyncio.AsyncIOMotorDatabase) -> None:
    await db.chord_progressions.delete_many({})
    await db.note_patterns.delete_many({})
    await db.rhythm_patterns.delete_many({})

async def format_chord_progression(name: str, progression: List[str]) -> Dict[str, Any]:
    if not progression:
        raise ValueError("Progression list cannot be empty.")

    chord_progressions = []
    for chord in progression:
        try:
            roman_numeral = RomanNumeral(scale_degree=RomanNumeral.ROMAN_TO_INT[chord], quality=ChordQualityType.MAJOR)
            chord_progressions.append(roman_numeral)
        except KeyError:
            raise ValueError(f"Invalid Roman numeral: {chord}")

    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'chords': [
            {
                'root': {'note_name': roman_numeral.get_note_name(), 'octave': 4},
                'quality': roman_numeral.quality
            } for roman_numeral in chord_progressions
        ],
        'key': DEFAULT_KEY,
        'scale_type': DEFAULT_SCALE_TYPE,
        'tags': ['preset'],
        'complexity': 1.0,
        'is_test': False,
        'index': 0
    }

async def format_note_pattern(name: str, pattern: dict) -> dict:
    """Format a note pattern according to the model requirements."""
    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'data': pattern['pattern'],
        'notes': [{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100} for _ in pattern['pattern']],
        'description': f'Pattern: {name}',
        'tags': ['preset'],
        'is_test': False,
        'index': pattern['index']
    }

async def format_rhythm_pattern(name: str, pattern: 'RhythmPatternData') -> dict:
    """Format a rhythm pattern according to the model requirements."""
    return {
        'id': str(uuid.uuid4()),
        'name': name,
        'pattern': pattern['pattern'],  
        'index': pattern['index'],  
        'description': f'Pattern: {name}',
        'tags': ['preset'],
        'is_test': False,
        'index': pattern['index']
    }

async def insert_data(db: motor_asyncio.AsyncIOMotorDatabase, data: list, collection_name: str) -> None:
    if data:
        result = await getattr(db, collection_name).insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} {collection_name}")

async def run_imports():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["note_gen"]
    
    await clear_existing_data(db)  # Clear existing data
    
    # Format and prepare all progressions
    chord_progressions = [
        await format_chord_progression(name, prog)
        for name, prog in COMMON_PROGRESSIONS.items()
    ]
    
    # Format and prepare all note patterns
    note_patterns = [
        await format_note_pattern(name, pattern)
        for name, pattern in NOTE_PATTERNS.items()
    ]
    
    # Format and prepare all rhythm patterns
    rhythm_patterns = [
        await format_rhythm_pattern(name, pattern)
        for name, pattern in RHYTHM_PATTERNS.items()
    ]
    
    # Insert the data
    await insert_data(db, chord_progressions, 'chord_progressions')
    await insert_data(db, note_patterns, 'note_patterns')
    await insert_data(db, rhythm_patterns, 'rhythm_patterns')
    
    print("Database population completed successfully")

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_imports())
