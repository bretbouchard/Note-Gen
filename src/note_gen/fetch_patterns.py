"""Functions for fetching patterns from the database."""

from typing import List, Optional, Dict, Any
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote
from note_gen.models.musical_elements import Chord, Note
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.enums import ChordQualityType
from note_gen.models.note_pattern import NotePattern
from note_gen.database import get_db
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

async def fetch_chord_progressions() -> List[ChordProgression]:
    """Fetch all chord progressions from the database."""
    async with get_db() as db:
        try:
            chord_progressions = []
            async for doc in db.chord_progressions.find({}):
                try:
                    # Convert chord quality strings to enum values
                    for chord in doc.get('chords', []):
                        if isinstance(chord, dict) and 'quality' in chord:
                            chord['quality'] = ChordQualityType[chord['quality']]
                    
                    progression = ChordProgression(**doc)
                    chord_progressions.append(progression)
                except Exception as e:
                    logger.error(f"Error creating ChordProgression from document: {e}")
                    continue
            return chord_progressions
        except Exception as e:
            logger.error(f"Error fetching chord progressions: {e}")
            return []

async def fetch_chord_progression_by_id(progression_id: str) -> Optional[ChordProgression]:
    """Fetch a chord progression by its ID."""
    async with get_db() as db:
        try:
            doc = await db.chord_progressions.find_one({"id": progression_id})
            if doc:
                # Convert chord quality strings to enum values
                for chord in doc.get('chords', []):
                    if isinstance(chord, dict) and 'quality' in chord:
                        chord['quality'] = ChordQualityType[chord['quality']]
                
                return ChordProgression(**doc)
        except Exception as e:
            logger.error(f"Error fetching chord progression {progression_id}: {e}")
        
        return None

async def fetch_rhythm_patterns() -> List[RhythmPattern]:
    """Fetch all rhythm patterns from the database."""
    async with get_db() as db:
        try:
            rhythm_patterns = []
            async for doc in db.rhythm_patterns.find({}):
                try:
                    # Convert pattern list to RhythmNote objects
                    if 'pattern' in doc and isinstance(doc['pattern'], list):
                        doc['pattern'] = [
                            RhythmNote(**note) if isinstance(note, dict) else note
                            for note in doc['pattern']
                        ]
                    
                    pattern = RhythmPattern(**doc)
                    rhythm_patterns.append(pattern)
                except Exception as e:
                    logger.error(f"Error creating RhythmPattern from document: {e}")
                    continue
            return rhythm_patterns
        except Exception as e:
            logger.error(f"Error fetching rhythm patterns: {e}")
            return []

async def fetch_rhythm_pattern_by_id(pattern_id: str) -> Optional[RhythmPattern]:
    """Fetch a rhythm pattern by its ID."""
    async with get_db() as db:
        try:
            doc = await db.rhythm_patterns.find_one({"id": pattern_id})
            if doc:
                # Convert pattern list to RhythmNote objects
                if 'pattern' in doc and isinstance(doc['pattern'], list):
                    doc['pattern'] = [
                        RhythmNote(**note) if isinstance(note, dict) else note
                        for note in doc['pattern']
                    ]
                
                return RhythmPattern(**doc)
        except Exception as e:
            logger.error(f"Error fetching rhythm pattern {pattern_id}: {e}")
        
        return None

async def fetch_note_patterns() -> List[NotePattern]:
    """Fetch all note patterns from the database."""
    async with get_db() as db:
        try:
            cursor = db.note_patterns.find({})
            documents = await cursor.to_list(None)
            return [NotePattern(**doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error fetching note patterns: {e}")
            return []

async def fetch_note_pattern_by_id(pattern_id: str) -> Optional[NotePattern]:
    """
    Fetch a note pattern by its ID from the database.
    
    Args:
        pattern_id: The ID of the pattern to fetch
        
    Returns:
        Optional[NotePattern]: The note pattern if found, None otherwise
    """
    async with get_db() as db:
        try:
            pattern = await db.note_patterns.find_one({"id": pattern_id})
            return NotePattern(**pattern) if pattern else None
        except Exception as e:
            logger.error(f"Error fetching note pattern by ID: {e}")
            return None

# Main execution
if __name__ == "__main__":
    pass