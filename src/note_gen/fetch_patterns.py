"""Functions for fetching patterns from the database."""

from typing import List, Optional, Dict, Any, Mapping
from motor.motor_asyncio import AsyncIOMotorDatabase as Database

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.database import get_db
import logging
logging.getLogger('src.note_gen.fetch_patterns').setLevel(logging.DEBUG)

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
async def fetch_chord_progressions(db: Database[Mapping[str, Any]]) -> List[ChordProgression]:
    try:
        cursor = db.chord_progressions.find({})
        progressions = []
        async for doc in cursor:
            progression = ChordProgression(**doc)  # Ensure ChordProgression is typed
            progressions.append(progression)
        return progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def _fetch_chord_progressions(db: Database[Mapping[str, Any]]) -> List[ChordProgression]:
    try:
        chord_progressions = []
        async for doc in db.chord_progressions.find({}):
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
async def fetch_chord_progression_by_id(id: str, db: Database[Mapping[str, Any]]) -> Optional[ChordProgression]:
    try:
        result = await db.chord_progressions.find_one({"_id": id})
        logger.debug(f"Fetched result: {result}")
        if result:
            logger.debug(f"Raw document from MongoDB: {result}")
            
            # Process chords first
            processed_chords: List[Chord] = []
            for chord_data in result['chords']:
                logger.debug(f"Processing chord: {chord_data}")
                # Create root note
                root_note_data: Dict[str, Any] = {
                    'note_name': str(chord_data['root']['note_name']),
                    'octave': int(chord_data['root']['octave']),
                    'duration': int(float(chord_data['root']['duration'])),
                    'velocity': 64
                }
                root_note = Note(**root_note_data)
                
                # Create chord notes
                chord_notes = []
                for note_data in chord_data['notes']:
                    note_data_dict: Dict[str, Any] = {
                        'note_name': str(note_data['note_name']),
                        'octave': int(note_data['octave']),
                        'duration': int(float(note_data['duration'])),
                        'velocity': 64
                    }
                    note = Note(**note_data_dict)
                    chord_notes.append(note)
                
                # Create Chord object
                chord_data_dict = {
                    'root': root_note,
                    'quality': ChordQualityType[chord_data['quality'].upper()],  # Ensure quality is of correct type
                    'notes': chord_notes,
                    'inversion': 0
                }
                chord = Chord(root=root_note, quality=ChordQualityType[chord_data['quality'].upper()], notes=chord_notes, inversion=0)
            
            # Create ChordProgression
            prog_data = {
                'id': str(result['id']),
                'name': str(result['name']),
                'complexity': int(float(result['complexity'])),
                'key': str(result['key']),
                'scale_type': str(result['scale_type']),
                'chords': processed_chords
            }
            logger.debug(f"prog_data types: id={type(prog_data['id'])}, name={type(prog_data['name'])}, complexity={type(prog_data['complexity'])}, key={type(prog_data['key'])}, scale_type={type(prog_data['scale_type'])}, chords={type(prog_data['chords'])}")
            logger.debug(f"prog_data values: id={prog_data['id']}, name={prog_data['name']}, complexity={prog_data['complexity']}, key={prog_data['key']}, scale_type={prog_data['scale_type']}, chords={prog_data['chords']}")
            logger.debug(f"prog_data values: id={prog_data['id']}, name={prog_data['name']}, complexity={prog_data['complexity']}, key={prog_data['key']}, scale_type={prog_data['scale_type']}, chords={prog_data['chords']}")
            prog = ChordProgression(**prog_data)
            
            logger.debug(f"Created ChordProgression: {prog}")
            return prog
            
        return None
    except Exception as e:
        logger.error(f"Error fetching chord progression by id {id}: {e}")
        logger.debug(f"Error details: {str(e)}")
        return None


async def _fetch_chord_progression_by_id(progression_id: str, db: Database[Mapping[str, Any]]) -> Optional[ChordProgression]:
    try:
        doc = await db.chord_progressions.find_one({"id": progression_id})
        if doc:
            # Process chords
            if 'chords' in doc and isinstance(doc['chords'], list):
                doc['chords'] = [process_chord_data(chord) for chord in doc['chords']]
            
            return ChordProgression(**doc)
    except Exception as e:
        logger.error(f"Error fetching chord progression by id {progression_id}: {e}")
        return None

async def fetch_rhythm_patterns(db: Optional[Database[Mapping[str, Any]]] = None) -> List[RhythmPattern]:
    """Fetch all rhythm patterns from the database."""
    if db is None:
        async with get_db() as db:
            return await _fetch_rhythm_patterns(db)
    return await _fetch_rhythm_patterns(db)

async def _fetch_rhythm_patterns(db: Database[Mapping[str, Any]]) -> List[RhythmPattern]:
    try:
        patterns = []
        async for doc in db.rhythm_patterns.find({}):
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

async def fetch_rhythm_pattern_by_id(pattern_id: str, db: Optional[Database[Mapping[str, Any]]] = None) -> Optional[RhythmPattern]:
    """Fetch a rhythm pattern by its ID."""
    if db is None:
        async with get_db() as db:
            return await _fetch_rhythm_pattern_by_id(pattern_id, db)
    return await _fetch_rhythm_pattern_by_id(pattern_id, db)

async def _fetch_rhythm_pattern_by_id(pattern_id: str, db: Database[Mapping[str, Any]]) -> Optional[RhythmPattern]:
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
        logger.error(f"Error fetching rhythm pattern by id {pattern_id}: {e}")
        return None

async def fetch_note_patterns(db: Optional[Database[Mapping[str, Any]]] = None) -> List[NotePattern]:
    """Fetch all note patterns from the database."""
    if db is None:
        async with get_db() as db:
            return await _fetch_note_patterns(db)
    return await _fetch_note_patterns(db)

async def _fetch_note_patterns(db: Database[Mapping[str, Any]]) -> List[NotePattern]:
    try:
        patterns = []
        async for doc in db.note_patterns.find({}):
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

async def fetch_note_pattern_by_id(pattern_id: str, db: Optional[Database[Mapping[str, Any]]] = None) -> Optional[NotePattern]:
    """Fetch a note pattern by its ID."""
    if db is None:
        async with get_db() as db:
            return await _fetch_note_pattern_by_id(pattern_id, db)
    return await _fetch_note_pattern_by_id(pattern_id, db)

async def _fetch_note_pattern_by_id(pattern_id: str, db: Database[Mapping[str, Any]]) -> Optional[NotePattern]:
    try:
        doc = await db.note_patterns.find_one({"id": pattern_id})
        if doc:
            return NotePattern(**doc)
        return None
    except Exception as e:
        logger.error(f"Error fetching note pattern by id {pattern_id}: {e}")
        return None

# Main execution
if __name__ == "__main__":
    pass