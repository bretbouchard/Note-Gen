"""Functions for fetching patterns from the database."""

from typing import List, Optional, Dict, Any, Mapping
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.note_pattern import NotePattern
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
        # Convert quality to enum if it's a string
        if 'quality' in chord_data:
            try:
                # Convert chord_data['quality'] to ChordQualityType if it's a string
                quality_value = chord_data['quality']
                if isinstance(quality_value, str):
                    quality_value = ChordQualityType[quality_value.upper()]  # Example conversion
                quality = ChordQualityType._missing_(cls=ChordQualityType, value=quality_value)
                if quality is None:
                    logger.warning(f"Invalid chord quality '{chord_data['quality']}', defaulting to major")
                    quality = ChordQualityType.MAJOR
            except Exception as e:
                logger.warning(f"Error processing chord quality '{chord_data['quality']}': {e}, defaulting to major")
                quality = ChordQualityType.MAJOR

            # Ensure quality is always a valid ChordQualityType
            if not isinstance(quality, ChordQualityType):
                quality = ChordQualityType.MAJOR  # Default to major if quality is invalid

            chord_data['quality'] = quality
        elif isinstance(chord_data['quality'], ChordQualityType):
            # Already a ChordQualityType, no need to convert
            pass
        else:
            logger.error(f"Invalid chord quality type: {type(chord_data['quality'])}")
            chord_data['quality'] = ChordQualityType.MAJOR  # Default to major if invalid
        
        # Process root note if it exists
        if 'root' in chord_data:
            if isinstance(chord_data['root'], dict):
                # If root is a dict with note_name nested inside
                if 'note_name' in chord_data['root'] and isinstance(chord_data['root']['note_name'], dict):
                    note_data = chord_data['root']['note_name']
                    chord_data['root'] = Note(
                        note_name=note_data.get('note_name', 'C'),
                        octave=note_data.get('octave', 4)
                    )
                # If root is a dict with direct note_name
                elif 'note_name' in chord_data['root']:
                    chord_data['root'] = Note(
                        note_name=chord_data['root']['note_name'],
                        octave=chord_data['root'].get('octave', 4)
                    )
            elif isinstance(chord_data['root'], str):
                # If root is a string, create a Note with default octave
                chord_data['root'] = Note(note_name=chord_data['root'])
            elif not isinstance(chord_data['root'], Note):
                logger.error(f"Invalid root note type: {type(chord_data['root'])}")
                chord_data['root'] = Note(note_name='C')  # Default to C if invalid
    
    return chord_data

# In fetch_patterns.py
# In fetch_patterns.py
async def fetch_chord_progressions(db: AsyncIOMotorDatabase) -> List[ChordProgression]:
    try:
        cursor = db.chord_progressions.find({})
        progressions = await cursor.to_list(length=None)
        if not progressions:
            logger.error("No chord progressions found in the database.")
            raise ValueError("No chord progressions found.")

        for chord in progressions:
            logger.debug(f"Validating chord progression: {chord}")
            if 'chords' not in chord:
                logger.error(f"Missing chords field in chord progression: {chord}")
                raise ValueError(f"Missing chords field in chord progression: {chord}")
            if not isinstance(chord['chords'], list):
                logger.error(f"Chords field is not a list in chord progression: {chord}")
                raise ValueError(f"Chords field is not a list in chord progression: {chord}")
            if len(chord['chords']) == 0:
                logger.error(f"Empty chords list in chord progression: {chord}")
                raise ValueError(f"Invalid chord progression data: Empty chords list in chord progression: {chord}")

            # Additional validation for each chord in the progression
            for chord_item in chord['chords']:
                if not isinstance(chord_item, dict):
                    logger.error(f"Invalid chord item in progression: {chord_item}")
                    raise ValueError(f"Invalid chord item in progression: {chord_item}")

        return [ChordProgression(**doc) for doc in progressions]
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def _fetch_chord_progressions(db: AsyncIOMotorDatabase) -> List[ChordProgression]:
    logger.debug(f"Type of db: {type(db)}")  # Log the type of db
    try:
        chord_progressions = []
        async for doc in db.chord_progressions.find({}):
            logger.debug(f"Fetched document from MongoDB: {doc}")  # Log the fetched document
            try:
                # Process chords
                if 'chords' in doc and isinstance(doc['chords'], list):
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

# In fetch_patterns.py, around line 148
async def fetch_chord_progression_by_id(id: str, db: AsyncIOMotorDatabase) -> Optional[ChordProgression]:
    try:
        logger.debug(f"Attempting to fetch chord progression with ID: {id}")
        result = await db.chord_progressions.find_one({"_id": id})
        logger.debug(f"Fetched result: {result}")
        if result:
            logger.debug(f"Raw document from MongoDB: {result}")
            
            # Process chords first
            if 'chords' in result and isinstance(result['chords'], list):
                processed_chords = [process_chord_data(chord) for chord in result['chords']]
            else:
                processed_chords = []  # Default to an empty list if not valid
            
            prog_data = {
                'id': str(result['id']),
                'name': str(result['name']),
                'complexity': int(float(result['complexity'])),
                'key': str(result['key']),
                'scale_type': str(result['scale_type']),
                'chords': processed_chords
            }
            logger.debug(f"prog_data types: id={{type(prog_data['id'])}}, name={{type(prog_data['name'])}}, complexity={{type(prog_data['complexity'])}}, key={{type(prog_data['key'])}}, scale_type={{type(prog_data['scale_type'])}}, chords={{type(prog_data['chords'])}}")
            logger.debug(f"prog_data values: id={{prog_data['id']}}, name={{prog_data['name']}}, complexity={{prog_data['complexity']}}, key={{prog_data['key']}}, scale_type={{prog_data['scale_type']}}, chords={{prog_data['chords']}}")
            prog = ChordProgression(**prog_data)
            return prog
        else:
            logger.warning(f"No chord progression found for ID: {id}")
            return None
    except Exception as e:
        logger.error(f"Error fetching chord progression by ID: {e}", exc_info=True)
        return None


async def _fetch_chord_progression_by_id(progression_id: str, db: AsyncIOMotorDatabase) -> Optional[ChordProgression]:
    try:
        doc = await db.chord_progressions.find_one({"id": progression_id})
        logger.debug(f"Fetched document from MongoDB: {doc}")  # Log the fetched document
        if doc:
            # Process chords
            if 'chords' in doc and isinstance(doc['chords'], list):
                doc['chords'] = [process_chord_data(chord) for chord in doc['chords']]
            
            return ChordProgression(**doc)
    except Exception as e:
        logger.error(f"Error fetching chord progression by id {progression_id}: {e}")
        return None

async def fetch_rhythm_patterns(db: AsyncIOMotorDatabase) -> List[RhythmPattern]:
    logger.debug(f"Type of db: {type(db)}")  # Log the type of db
    """Fetch all rhythm patterns from the database."""
    try:
        cursor = db.rhythm_patterns.find({})
        patterns = await cursor.to_list(length=None)
        return [RhythmPattern(**doc) for doc in patterns]
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

async def _fetch_rhythm_patterns(db: AsyncIOMotorDatabase) -> List[RhythmPattern]:
    try:
        patterns = []
        async for doc in db.rhythm_patterns.find({}):
            logger.debug(f"Fetched document from MongoDB: {doc}")  # Log the fetched document
            try:
                # Convert pattern list to RhythmNote objects
                if 'pattern' in doc and isinstance(doc['pattern'], list):
                    doc['pattern'] = [
                        RhythmNote(**note) if isinstance(note, dict) else note
                        for note in doc['pattern']
                    ]
                
                pattern = RhythmPattern(**doc)
                patterns.append(pattern)
            except Exception as e:
                logger.error(f"Error creating RhythmPattern from document: {e}")
                continue
        return patterns
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

async def fetch_rhythm_pattern_by_id(pattern_id: str, db: Optional[AsyncIOMotorDatabase] = None) -> Optional[RhythmPattern]:
    logger.debug(f"Type of db: {type(db)}")  # Log the type of db
    """Fetch a rhythm pattern by its ID."""
    if db is None:
        async with get_db() as db:
            return await _fetch_rhythm_pattern_by_id(pattern_id, db)
    return await _fetch_rhythm_pattern_by_id(pattern_id, db)

async def _fetch_rhythm_pattern_by_id(pattern_id: str, db: AsyncIOMotorDatabase) -> Optional[RhythmPattern]:
    try:
        doc = await db.rhythm_patterns.find_one({"id": pattern_id})
        logger.debug(f"Fetched document from MongoDB: {doc}")  # Log the fetched document
        if doc:
            # Convert pattern list to RhythmNote objects
            if 'pattern' in doc and isinstance(doc['pattern'], list):
                doc['pattern'] = [
                    RhythmNote(**note) if isinstance(note, dict) else note
                    for note in doc['pattern']
                ]
            
            return RhythmPattern(**doc)
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern by id {pattern_id}: {e}")
        return None

async def fetch_note_patterns(db: Optional[AsyncIOMotorDatabase] = None) -> List[NotePattern]:
    logger.debug(f"Type of db: {type(db)}")  # Log the type of db
    """Fetch all note patterns from the database."""
    if db is None:
        async with get_db() as db:
            return await _fetch_note_patterns(db)
    return await _fetch_note_patterns(db)

async def _fetch_note_patterns(db: AsyncIOMotorDatabase) -> List[NotePattern]:
    try:
        patterns = []
        async for doc in db.note_patterns.find({}):
            logger.debug(f"Fetched document from MongoDB: {doc}")  # Log the fetched document
            logger.debug(f"Fetched document: {doc}")  # Log the fetched document
            try:
                # Log the keys in the document for debugging
                logger.debug(f"Document keys: {list(doc.keys())}")
                # Log the entire document for clarity
                logger.debug(f"Full document content: {doc}")
                # Filter out unexpected fields
                valid_fields = {key: doc[key] for key in doc if key in NotePattern.__fields__}
                logger.debug(f"Valid fields for NotePattern: {valid_fields}")  # Log valid fields
                pattern = NotePattern(**valid_fields)
                patterns.append(pattern)
            except Exception as e:
                logger.error(f"Error creating NotePattern from document: {e}")
                continue
        logger.debug(f"Final patterns list: {patterns}")  # Log the final patterns list
        return patterns
    except Exception as e:
        logger.error(f"Error fetching note patterns: {e}")
        return []

async def fetch_note_pattern_by_id(pattern_id: str, db: Optional[AsyncIOMotorDatabase] = None) -> Optional[NotePattern]:
    logger.debug(f"Type of db: {type(db)}")  # Log the type of db
    """Fetch a note pattern by its ID."""
    if db is None:
        async with get_db() as db:
            return await _fetch_note_pattern_by_id(pattern_id, db)
    return await _fetch_note_pattern_by_id(pattern_id, db)

async def _fetch_note_pattern_by_id(pattern_id: str, db: AsyncIOMotorDatabase) -> Optional[NotePattern]:
    try:
        doc = await db.note_patterns.find_one({"id": pattern_id})
        logger.debug(f"Fetched document from MongoDB: {doc}")  # Log the fetched document
        if doc:
            return NotePattern(**doc)
        return None
    except Exception as e:
        logger.error(f"Error fetching note pattern by id {pattern_id}: {e}")
        return None

# Main execution
if __name__ == "__main__":
    pass