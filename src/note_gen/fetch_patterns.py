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
        documents = [ChordProgression(**doc) for doc in db.chord_progressions.find()]
        logger.debug(f'Retrieved {len(documents)} chord progressions.')
        return documents
    except Exception as e:
        logger.error(f'Error fetching chord progressions: {e}')
        return []

# Function to fetch note patterns

def fetch_note_patterns() -> List[NotePattern]:
    try:
        documents = [NotePattern(**doc) for doc in db.note_patterns.find()]
        logger.debug(f'Retrieved {len(documents)} note patterns from the database.')
        logger.info(f'Number of note patterns retrieved: {len(documents)}')
        return documents
    except Exception as e:
        logger.error(f'Error fetching note patterns: {e}')
        return []

# Function to fetch rhythm patterns

def fetch_rhythm_patterns() -> List[RhythmPattern]:
    try:
        documents = [RhythmPattern(**doc) for doc in db.rhythm_patterns.find()]
        logger.debug(f'Retrieved {len(documents)} rhythm patterns.')
        return documents
    except Exception as e:
        logger.error(f'Error fetching rhythm patterns: {e}')
        return []

# Function to fetch chord progression by ID

def fetch_chord_progression_by_id(id: int) -> Optional[ChordProgression]:
    try:
        document = db.chord_progressions.find_one({"id": str(id)})  # Adjusting query to match string ID
        if document:
            logger.debug(f'Fetched chord progression with ID {id}.')
            return ChordProgression(**document)
        else:
            logger.warning(f'No chord progression found with ID {id}.')
            return None
    except Exception as e:
        logger.error(f'Error fetching chord progression by ID {id}: {e}')
        return None

# Function to fetch note pattern by ID

def fetch_note_pattern_by_id(id: int) -> Optional[NotePattern]:
    try:
        document = db.note_patterns.find_one({"id": id})  # Adjust the query as necessary
        if document:
            logger.debug(f'Fetched note pattern with ID {id}.')
            return NotePattern(**document)
        else:
            logger.warning(f'No note pattern found with ID {id}.')
            return None
    except Exception as e:
        logger.error(f'Error fetching note pattern by ID {id}: {e}')
        return None

# Function to fetch rhythm pattern by ID

def fetch_rhythm_pattern_by_id(id: int) -> Optional[RhythmPattern]:
    try:
        document = db.rhythm_patterns.find_one({"id": str(id)})  # Adjusting query to match string ID
        if document:
            logger.debug(f'Fetched rhythm pattern with ID {id}.')
            rhythm_data = RhythmPatternData(**document['data'])
            return RhythmPattern(name=document['name'], data=rhythm_data, description=document.get('description', ''), tags=document.get('tags', []))
        else:
            logger.warning(f'No rhythm pattern found with ID {id}.')
            return None
    except Exception as e:
        logger.error(f'Error fetching rhythm pattern by ID {id}: {e}')
        return None

# Main execution
if __name__ == "__main__":
    pass