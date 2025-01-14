import pymongo
import logging
from src.note_gen.models.presets import DEFAULT_CHORD_PROGRESSION, DEFAULT_NOTE_PATTERN, COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern  # Import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData  # Import RhythmPattern and RhythmPatternData
from typing import List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB connection
client: pymongo.MongoClient = pymongo.MongoClient("mongodb://localhost:27017/")  # type: ignore
db = client["note_gen"]  # Use your database name

# Function to fetch chord progressions

def fetch_chord_progressions() -> List[ChordProgression]:
    try:
        documents = db.chord_progressions.find()
        logger.debug(f"Fetched chord progressions: {list(documents)}")
        return [ChordProgression(scale_info=doc['scale_info'], chords=doc['chords']) for doc in documents if 'scale_info' in doc and 'chords' in doc]
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

# Function to fetch note patterns

def fetch_note_patterns() -> List[NotePattern]:
    try:
        documents = db.note_patterns.find()
        logger.debug(f"Fetched note patterns: {list(documents)}")
        return [NotePattern(name=doc['name'], data=doc['data']) for doc in documents if 'name' in doc and 'data' in doc]
    except Exception as e:
        logger.error(f"Error fetching note patterns: {e}")
        return []

# Function to fetch rhythm patterns

def fetch_rhythm_patterns() -> List[RhythmPattern]:
    try:
        documents = db.rhythm_patterns.find()
        logger.debug(f"Fetched rhythm patterns: {list(documents)}")
        return [RhythmPattern(id=str(doc['_id']), name=doc['name'], data=RhythmPatternData(**doc['data'])) for doc in documents if 'name' in doc and 'data' in doc]
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

# Function to fetch chord progression by ID

def fetch_chord_progression_by_id(id: int) -> Optional[ChordProgression]:
    try:
        document = db.chord_progressions.find_one({"id": id})
        if document:
            logger.debug(f'Fetched chord progression with ID {id}.')
            return ChordProgression(
                scale_info=document['scale_info'],
                chords=document['progression'],
                root=document.get('root')
            )
        else:
            logger.warning(f'No chord progression found with ID {id}.')
            return None
    except Exception as e:
        logger.error(f'Error fetching chord progression by ID {id}: {e}')
        return None

# Function to fetch note pattern by ID

def fetch_note_pattern_by_id(id: int) -> Optional[NotePattern]:
    try:
        document = db.note_patterns.find_one({"id": id})
        if document:
            logger.debug(f'Fetched note pattern with ID {id}.')
            return NotePattern(
                name=document['name'],
                data=document['pattern'],
                description=document.get('description', ''),
                tags=document.get('tags', [])
            )
        else:
            logger.warning(f'No note pattern found with ID {id}.')
            return None
    except Exception as e:
        logger.error(f'Error fetching note pattern by ID {id}: {e}')
        return None

# Function to fetch rhythm pattern by ID

def fetch_rhythm_pattern_by_id(id: int) -> Optional[RhythmPattern]:
    try:
        document = db.rhythm_patterns.find_one({"id": id})
        if document:
            logger.debug(f'Fetched rhythm pattern with ID {id}.')
            rhythm_data = RhythmPatternData(
                notes=document['pattern'].get('notes', []),
                time_signature=document['pattern'].get('time_signature', '4/4'),
                swing_enabled=document['pattern'].get('swing_enabled', False),
                humanize_amount=document['pattern'].get('humanize_amount', 0.0),
                swing_ratio=document['pattern'].get('swing_ratio', 0.67),
                style=document['pattern'].get('style'),
                default_duration=document['pattern'].get('default_duration', 1.0),
                total_duration=document['pattern'].get('total_duration', 0.0),
                accent_pattern=document['pattern'].get('accent_pattern'),
                groove_type=document['pattern'].get('groove_type'),
                variation_probability=document['pattern'].get('variation_probability', 0.0),
                duration=document['pattern'].get('duration', 1.0)
            )
            return RhythmPattern(
                id=str(document['id']),
                name=document['name'],
                data=rhythm_data,
                description=document.get('description', ''),
                tags=document.get('tags', []),
                complexity=document.get('complexity', 1.0),
                style=document.get('style'),
                pattern=document.get('pattern', '')
            )
        else:
            logger.warning(f'No rhythm pattern found with ID {id}.')
            return None
    except Exception as e:
        logger.error(f'Error fetching rhythm pattern by ID {id}: {e}')
        return None

# Main execution
if __name__ == "__main__":
    pass