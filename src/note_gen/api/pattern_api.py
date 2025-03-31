"""Pattern API functions for fetching and managing patterns."""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.patterns import ChordProgressionPattern, NotePattern, RhythmPattern
from ..core.constants import COLLECTION_NAMES

async def fetch_chord_progressions(db: AsyncIOMotorDatabase) -> List[ChordProgressionPattern]:
    """Fetch all chord progressions from the database."""
    cursor = db[COLLECTION_NAMES["chord_progressions"]].find({})
    progressions = await cursor.to_list(length=None)
    return [ChordProgressionPattern(**prog) for prog in progressions]

async def fetch_chord_progression_by_id(
    db: AsyncIOMotorDatabase,
    progression_id: str
) -> Optional[ChordProgressionPattern]:
    """Fetch a specific chord progression by ID."""
    prog = await db[COLLECTION_NAMES["chord_progressions"]].find_one({"id": progression_id})
    return ChordProgressionPattern(**prog) if prog else None

async def fetch_rhythm_patterns(db: AsyncIOMotorDatabase) -> List[RhythmPattern]:
    """Fetch all rhythm patterns from the database."""
    cursor = db[COLLECTION_NAMES["rhythm_patterns"]].find({})
    patterns = await cursor.to_list(length=None)
    return [RhythmPattern(**pattern) for pattern in patterns]

async def fetch_rhythm_pattern_by_id(
    db: AsyncIOMotorDatabase,
    pattern_id: str
) -> Optional[RhythmPattern]:
    """Fetch a specific rhythm pattern by ID."""
    pattern = await db[COLLECTION_NAMES["rhythm_patterns"]].find_one({"id": pattern_id})
    return RhythmPattern(**pattern) if pattern else None

async def fetch_note_patterns(db: AsyncIOMotorDatabase) -> List[NotePattern]:
    """Fetch all note patterns from the database."""
    cursor = db[COLLECTION_NAMES["note_patterns"]].find({})
    patterns = await cursor.to_list(length=None)
    return [NotePattern(**pattern) for pattern in patterns]

async def fetch_note_pattern_by_id(
    db: AsyncIOMotorDatabase,
    pattern_id: str
) -> Optional[NotePattern]:
    """Fetch a specific note pattern by ID."""
    pattern = await db[COLLECTION_NAMES["note_patterns"]].find_one({"id": pattern_id})
    return NotePattern(**pattern) if pattern else None

async def check_rhythm_pattern(pattern: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a rhythm pattern structure and return validation results.
    
    Args:
        pattern: Dictionary containing rhythm pattern data
        
    Returns:
        Dictionary containing validation results
    """
    try:
        rhythm_pattern = RhythmPattern(**pattern)
        validation_result = rhythm_pattern.validate_pattern()
        return {
            "valid": validation_result.is_valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": []
        }
