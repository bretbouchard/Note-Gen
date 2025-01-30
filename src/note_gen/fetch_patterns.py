"""Functions for fetching patterns from the database."""

from typing import List, Optional, Dict, Any, Mapping
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.note_pattern import NotePatternResponse as NotePattern
from src.note_gen.database import get_db
import logging
import sys

# Configure logging for asynchronous operations
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

def process_chord_data(chord_data: Dict[str, Any], db_name: str) -> Dict[str, Any]:
    """Process chord data from the database."""
    logger.debug(f"Processing chord data for database: {db_name}")
    logger.debug(f"Input chord data: {chord_data}")

    # If we're processing a single chord object
    if 'root' in chord_data:
        return chord_data

    # If we're processing a chord progression
    if 'chords' in chord_data:
        if not isinstance(chord_data['chords'], list) or len(chord_data['chords']) == 0:
            logger.error("Chords must be a non-empty list.")
            raise ValueError("Chords must be a non-empty list.")
        
        # Process each chord in the progression
        processed_chords = []
        for chord in chord_data['chords']:
            if not isinstance(chord, dict):
                logger.error(f"Invalid chord format: {chord}")
                raise ValueError(f"Invalid chord format: {chord}")
            processed_chords.append(chord)
        
        chord_data['chords'] = processed_chords
        return chord_data

    logger.error("Invalid chord data format")
    raise ValueError("Invalid chord data format")

async def fetch_chord_progressions(db: AsyncIOMotorDatabase[Dict[str, Any]]) -> List[ChordProgression]:
    if db is None:
        raise RuntimeError("Database connection is not available.")
    try:
        cursor = db.chord_progressions.find({})
        fetched_progressions = await cursor.to_list(length=None)
        logger.debug(f'Fetched chord progressions: {fetched_progressions}')  
        # Convert fetched data to ChordProgression instances
        return [ChordProgression(**progression) for progression in fetched_progressions]
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def _fetch_chord_progressions(db: AsyncIOMotorDatabase[Dict[str, Any]]) -> List[ChordProgression]:
    logger.debug(f"Type of db: {type(db)}")  
    try:
        chord_progressions = []
        async for doc in db.chord_progressions.find({}):
            logger.debug(f"Fetched document from MongoDB: {doc}")  
            try:
                # Process chords
                if isinstance(doc, dict) and 'chords' in doc and isinstance(doc['chords'], list) and isinstance(doc, dict):
                    doc['chords'] = [process_chord_data(chord, db_name=db.name) for chord in doc['chords']]
                progression = ChordProgression(**doc)
                chord_progressions.append(progression)
            except Exception as e:
                logger.error(f"Error creating ChordProgression from document: {e}")
                continue
        return chord_progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def fetch_chord_progression_by_id(id: str, db: AsyncIOMotorDatabase[Dict[str, Any]]) -> Optional[ChordProgression]:
    """Fetch a chord progression by ID from the database."""
    try:
        logger.debug(f"Attempting to fetch chord progression with ID: {id}")
        result = await db.chord_progressions.find_one({'id': id})
        
        if result is None:
            logger.debug(f"No chord progression found with ID: {id}")
            return None

        # Log the chords before processing
        logger.debug(f"Chords retrieved: {result.get('chords', [])}")
        
        # Process the entire chord progression data
        processed_data = process_chord_data(result, db.name)
        
        # Create and return the ChordProgression instance
        return ChordProgression(**processed_data)
    except Exception as e:
        logger.error(f"Error fetching chord progression by ID: {id}, Error: {str(e)}")
        return None

async def _fetch_chord_progression_by_id(progression_id: str, db: AsyncIOMotorDatabase[Dict[str, Any]]) -> Optional[ChordProgression]:
    try:
        logger.debug(f"Attempting to fetch chord progression with ID: {progression_id}")
        result = await db.chord_progressions.find_one({"id": progression_id})
        logger.debug(f'Fetched result: {result}')

        # Log all chord progressions in the database
        all_progressions = await db.chord_progressions.find().to_list(None)
        logger.debug(f'All chord progressions in the database: {all_progressions}')

        if result:
            # Process chords
            if isinstance(result, dict) and 'chords' in result and isinstance(result['chords'], list) and isinstance(result, dict):
                result['chords'] = [process_chord_data(chord, db_name=db.name) for chord in result['chords']]
            
            return ChordProgression(**result)
        return None
    except Exception as e:
        logger.error(f"Error fetching chord progression by id {progression_id}: {e}")
        return None

async def fetch_rhythm_patterns(db: AsyncIOMotorDatabase[Dict[str, Any]]) -> List[RhythmPattern]:
    logger.debug(f"Type of db: {type(db)}")  
    if db is None:
        raise RuntimeError("Database connection is not available.")
    try:
        cursor = db.rhythm_patterns.find({})
        fetched_patterns = await cursor.to_list(length=None)
        logger.debug(f'Fetched rhythm patterns: {fetched_patterns}')  
        return [RhythmPattern(**pattern) for pattern in fetched_patterns]
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

async def _fetch_rhythm_patterns(db: AsyncIOMotorDatabase[Dict[str, Any]]) -> List[RhythmPattern]:
    logger.debug(f"Type of db: {type(db)}")  
    try:
        patterns = []
        async for doc in db.rhythm_patterns.find({}):
            logger.debug(f"Fetched document from MongoDB: {doc}")  
            try:
                pattern = RhythmPattern(**doc)
                patterns.append(pattern)
            except Exception as e:
                logger.error(f"Error creating RhythmPattern from document: {e}")
                continue
        return patterns
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

async def fetch_rhythm_pattern_by_id(pattern_id: str, db: Optional[AsyncIOMotorDatabase[Any]] = None) -> Optional[RhythmPattern]:
    logger.debug(f"Type of db: {type(db)}")  
    """Fetch a rhythm pattern by its ID."""
    if db is None:
        async with get_db() as db:
            return await _fetch_rhythm_pattern_by_id(pattern_id, db)
    return await _fetch_rhythm_pattern_by_id(pattern_id, db)

async def _fetch_rhythm_pattern_by_id(pattern_id: str, db: AsyncIOMotorDatabase[Dict[str, Any]]) -> Optional[RhythmPattern]:
    try:
        doc = await db.rhythm_patterns.find_one({"id": pattern_id})
        logger.debug(f"Fetched document from MongoDB: {doc}")  
        if doc:
            return RhythmPattern(**doc)
        return None
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern by id {pattern_id}: {e}")
        return None

async def fetch_note_patterns(db: Optional[AsyncIOMotorDatabase[Dict[str, Any]]] = None) -> List[NotePattern]:
    logger.debug(f"Type of db: {type(db)}")  
    """Fetch all note patterns from the database."""
    if db is None:
        async with get_db() as db:
            return await _fetch_note_patterns(db)
    return await _fetch_note_patterns(db)

async def _fetch_note_patterns(db: AsyncIOMotorDatabase[Dict[str, Any]]) -> List[NotePattern]:
    try:
        patterns = []
        async for doc in db.note_patterns.find({}):
            logger.debug(f"Fetched document from MongoDB: {doc}")  
            logger.debug(f"Fetched document: {doc}")  
            try:
                if doc is not None and isinstance(doc, dict):
                    # Log the keys in the document for debugging
                    logger.debug(f"Document keys: {list(doc.keys())}")
                    # Log the entire document for clarity
                    logger.debug(f"Full document content: {doc}")
                    # Filter out unexpected fields
                    valid_fields = {key: doc[key] for key in NotePattern.__annotations__.keys() if key in doc}
                    logger.debug(f"Valid fields for NotePattern: {valid_fields}")  
                    pattern = NotePattern(**valid_fields)
                    patterns.append(pattern)
            except Exception as e:
                logger.error(f"Error creating NotePattern from document: {e}")
                continue
        logger.debug(f"Final patterns list: {patterns}")  
        return patterns
    except Exception as e:
        logger.error(f"Error fetching note patterns: {e}")
        return patterns

async def fetch_note_pattern_by_id(pattern_id: str, db: Optional[AsyncIOMotorDatabase[Any]] = None) -> Optional[NotePattern]:
    logger.debug(f"Type of db: {type(db)}")  
    """Fetch a note pattern by its ID."""
    if db is None:
        async with get_db() as db:
            return await _fetch_note_pattern_by_id(pattern_id, db)
    return await _fetch_note_pattern_by_id(pattern_id, db)

async def _fetch_note_pattern_by_id(pattern_id: str, db: AsyncIOMotorDatabase[Dict[str, Any]]) -> Optional[NotePattern]:
    try:
        doc = await db.note_patterns.find_one({"id": pattern_id})
        logger.debug(f"Fetched document from MongoDB: {doc}")  
        if doc:
            return NotePattern(**doc)
        return None
    except Exception as e:
        logger.error(f"Error fetching note pattern by id {pattern_id}: {e}")
        return None

# Main execution
if __name__ == "__main__":
    pass