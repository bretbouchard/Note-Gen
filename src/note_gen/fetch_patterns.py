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

def process_chord_data(chord_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process chord data to handle nested structures."""
    # Check if chord_data is a dictionary
    if isinstance(chord_data, dict):
        # Process root note if it exists
        if isinstance(chord_data, dict) and 'root' in chord_data and isinstance(chord_data, dict):
            if isinstance(chord_data['root'], dict) and 'note_name' in chord_data['root'] and isinstance(chord_data['root'], dict):
                note_data = chord_data['root']
                chord_data['root'] = Note(
                    note_name=note_data.get('note_name', 'C'),
                    octave=note_data.get('octave')  # Dynamically assign octave from note_data if available
                )
            elif isinstance(chord_data['root'], str):
                chord_data['root'] = Note(note_name=chord_data['root'], octave=4)  # Default octave set to 4
            elif not isinstance(chord_data['root'], Note):
                logger.error(f"Invalid root note type: {type(chord_data['root'])}")
                chord_data['root'] = Note(note_name='C', octave=4)  # Default to C if invalid

        # Update the logic to convert chord quality strings to enums and vice versa
        if isinstance(chord_data, dict) and 'quality' in chord_data and isinstance(chord_data, dict):
            chord_quality = chord_data['quality']
            if isinstance(chord_quality, str):
                try:
                    chord_data['quality'] = ChordQualityType[chord_quality.upper()]
                except KeyError:
                    logger.error(f"Invalid chord quality string: {chord_quality}")
                    chord_data['quality'] = ChordQualityType.MAJOR  # Default to MAJOR if invalid
            elif not isinstance(chord_quality, ChordQualityType):
                logger.warning('Invalid chord quality type, defaulting to MAJOR.')
                chord_data['quality'] = ChordQualityType.MAJOR
    
    return chord_data

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
                    doc['chords'] = [process_chord_data(chord) for chord in doc['chords']]
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
    try:
        logger.debug(f"Attempting to fetch chord progression with ID: {id}")
        result = await db.chord_progressions.find_one({"_id": id})
        logger.debug(f"Fetched result: {result}")
        if result and isinstance(result, dict):
            logger.debug(f"Raw document from MongoDB: {result}")
            # Process chords first
            processed_chords = [process_chord_data(chord) for chord in result.get('chords', [])]
            prog_data: Dict[str, Any] = {
                'id': str(result.get('id', '')),  
                'name': str(result['name']),  
                'complexity': float(result.get('complexity', 0.0)),  
                'key': str(result['key']),  
                'scale_type': str(result['scale_type']),  
                'chords': processed_chords
            }
            logger.debug(f"prog_data types: id={{type(prog_data['id'])}}, name={{type(prog_data['name'])}}, complexity={{type(prog_data['complexity'])}}, key={{type(prog_data['key'])}}, scale_type={{type(prog_data['scale_type'])}}, chords={{type(prog_data['chords'])}}")
            logger.debug(f"prog_data values: id={{prog_data['id']}}, name={{prog_data['name']}}, complexity={{prog_data['complexity']}}, key={{prog_data['key']}}, scale_type={{prog_data['scale_type']}}, chords={{prog_data['chords']}}")
            return ChordProgression(**prog_data)
        else:
            logger.warning(f"No chord progression found for ID: {id}")
            return None
    except Exception as e:
        logger.error(f"Error fetching chord progression by ID: {e}", exc_info=True)
        return None

async def _fetch_chord_progression_by_id(progression_id: str, db: AsyncIOMotorDatabase[Dict[str, Any]]) -> Optional[ChordProgression]:
    try:
        doc = await db.chord_progressions.find_one({"id": progression_id})
        logger.debug(f"Fetched document from MongoDB: {doc}")  
        if doc:
            # Process chords
            if isinstance(doc, dict) and 'chords' in doc and isinstance(doc['chords'], list) and isinstance(doc, dict):
                doc['chords'] = [process_chord_data(chord) for chord in doc['chords']]
            
            return ChordProgression(**doc)
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