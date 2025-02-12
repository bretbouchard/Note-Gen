"""Functions for fetching patterns from the database."""

from typing import List, Optional, Dict, Any, Mapping, Union
from motor.motor_asyncio import AsyncIOMotorDatabase
import motor.motor_asyncio
import re
import uuid
import random
import logging
import sys
from pydantic import ValidationError, Field

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ChordQualityType, ScaleType
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.database.db import get_db_connection
from tests.conftest import MockDatabase

# Configure logging for asynchronous operations
logger = logging.getLogger(__name__)

def process_chord_data(chord_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process chord data, converting root to a Note instance and handling other transformations.
    
    Args:
        chord_data (Dict[str, Any]): Raw chord data from the database.
    
    Returns:
        Dict[str, Any]: Processed chord data with proper Note instances and defaults.
    
    Raises:
        ValueError: If required fields are missing or invalid.
    """
    try:
        # Validate input is a dictionary
        if not isinstance(chord_data, dict):
            raise ValueError(f"Expected dictionary, got {type(chord_data)}")
        
        # Create a copy to avoid modifying the original
        processed_data = chord_data.copy()
        
        # Validate required fields
        required_fields = ['id', 'name', 'chords', 'key', 'scale_type']
        for field in required_fields:
            if field not in processed_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Normalize the ID field
        processed_data['id'] = str(processed_data.get('id', ''))
        
        # Process chords with enhanced validation
        if not isinstance(processed_data['chords'], list):
            raise ValueError("Chords must be a list")
        
        processed_chords = []
        for chord in processed_data['chords']:
            # Validate chord structure
            if not isinstance(chord, dict):
                raise ValueError(f"Invalid chord structure: {chord}")
            
            root = chord.get('root', {})
            if not isinstance(root, dict):
                raise ValueError(f"Invalid root structure: {root}")
            
            # Ensure root has required keys with defaults
            note_name = root.get('note_name', '')
            octave = root.get('octave', 4)
            
            if not note_name:
                raise ValueError("Note name is required for each chord")
            
            # Create Note instance with robust defaults
            note = Note(
                note_name=note_name,
                octave=octave,
                duration=root.get('duration', 1.0),
                velocity=root.get('velocity', 100)
            )
            
            # Create Chord instance with error handling
            try:
                chord_copy = Chord(
                    root=note,
                    quality=ChordQualityType(chord.get('quality', 'MAJOR'))
                )
                processed_chords.append(chord_copy)
            except ValueError as ve:
                logger.warning(f"Invalid chord quality, defaulting to MAJOR: {ve}")
                chord_copy = Chord(root=note, quality=ChordQualityType.MAJOR)
                processed_chords.append(chord_copy)
        
        processed_data['chords'] = processed_chords
        
        # Process scale_info with enhanced validation
        if 'scale_info' in processed_data:
            scale_info = processed_data['scale_info']
            if not isinstance(scale_info, dict):
                raise ValueError(f"Invalid scale_info structure: {scale_info}")
            
            scale_root = scale_info.get('root', {})
            if not isinstance(scale_root, dict):
                raise ValueError(f"Invalid scale root structure: {scale_root}")
            
            note = Note(
                note_name=scale_root.get('note_name', ''),
                octave=scale_root.get('octave', 4),
                duration=scale_root.get('duration', 1.0),
                velocity=scale_root.get('velocity', 100)
            )
            
            processed_data['scale_info'] = ScaleInfo(
                root=note,
                scale_type=ScaleType(scale_info.get('scale_type', 'MAJOR'))
            )
        
        return processed_data
    
    except (ValueError, TypeError) as e:
        logger.error(f"Error processing chord progression: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing chord progression: {e}")
        raise

async def fetch_chord_progressions(db: Optional[AsyncIOMotorDatabase[Dict[str, Any]]] = None) -> List[ChordProgression]:
    """Fetch all chord progressions from the database."""
    try:
        if db is None:
            db = await get_db_connection()
        
        cursor = db.chord_progressions.find({})
        fetched_progressions = await cursor.to_list(length=None)
        
        processed_progressions = []
        for progression in fetched_progressions:
            try:
                # Process the chord data
                processed_data = process_chord_data(progression)
                # Create ChordProgression instance
                chord_progression = ChordProgression(**processed_data)
                processed_progressions.append(chord_progression)
            except ValidationError as ve:
                logger.error(f"Validation error processing chord progression: {ve}")
                continue
            except Exception as e:
                logger.error(f"Error processing chord progression: {e}")
                continue
                
        return processed_progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def fetch_chord_progression_by_id(chord_progression_id: str, db: Optional[AsyncIOMotorDatabase[Dict[str, Any]]] = None) -> Optional[ChordProgression]:
    """Fetch a specific chord progression by its ID."""
    try:
        if db is None:
            db = await get_db_connection()
        
        result = await db.chord_progressions.find_one({"id": chord_progression_id})
        if result is None:
            logger.error(f"No chord progression found with ID: {chord_progression_id}")
            return None
        
        # Process the chord data
        processed_data = process_chord_data(result)
        return ChordProgression(**processed_data)
    except ValidationError as ve:
        logger.error(f"Validation error fetching chord progression by id {chord_progression_id}: {ve}")
        return None
    except Exception as e:
        logger.error(f"Error fetching chord progression by id {chord_progression_id}: {e}")
        return None

async def fetch_rhythm_patterns(
    db: motor.motor_asyncio.AsyncIOMotorDatabase,
    query: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None
) -> List[RhythmPattern]:
    """
    Fetch rhythm patterns from the database with improved error handling.
    
    Args:
        db (motor.motor_asyncio.AsyncIOMotorDatabase): The MongoDB database connection.
        query: Optional query to filter rhythm patterns
        limit: Optional limit on number of patterns to fetch
        skip: Optional number of patterns to skip
    
    Returns:
        List[RhythmPattern]: A list of validated rhythm patterns.
    
    Raises:
        ValueError: If a rhythm pattern fails validation.
    """
    try:
        # Use default query if none provided
        query = query or {}
        
        # Fetch the cursor
        cursor = db.rhythm_patterns.find(query)
        
        # Apply limit if specified
        if limit is not None:
            cursor.limit(limit)
        
        # Apply skip if specified
        if skip is not None:
            cursor.skip(skip)
        
        # Handle different types of cursor/generator
        if hasattr(cursor, 'to_list'):
            results = await cursor.to_list(length=None)
        else:
            # For mock database or async generators
            results = [result async for result in cursor]
        
        validated_patterns: List[RhythmPattern] = []
        for result in results:
            try:
                rhythm_pattern = RhythmPattern(**result)
                validated_patterns.append(rhythm_pattern)
            
            except ValidationError as ve:
                logger.error(f"Validation error for rhythm pattern: {ve}")
                continue
            except Exception as e:
                logger.error(f"Error processing rhythm pattern: {e}")
                continue
        
        return validated_patterns
    
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

async def fetch_rhythm_pattern_by_id(
    pattern_id: str, 
    db: Union[motor.motor_asyncio.AsyncIOMotorDatabase, Any] = None
) -> Optional[RhythmPattern]:
    """
    Fetch a specific rhythm pattern by its ID with comprehensive validation.
    
    Args:
        pattern_id: The unique identifier of the rhythm pattern.
        db: MongoDB database connection or MockDatabase
    
    Returns:
        A validated rhythm pattern or None if not found or invalid.
    """
    try:
        # Handle different database types
        if db is None:
            db = await get_db_connection()
        
        # Check if db is a MockDatabase or has a rhythm_patterns attribute
        if hasattr(db, 'rhythm_patterns'):
            result = await db.rhythm_patterns.find_one({"id": pattern_id})
        else:
            result = await db.rhythm_patterns.find_one({"id": pattern_id})
        
        # Return None if no pattern found
        if result is None:
            logger.error(f"No rhythm pattern found with ID: {pattern_id}")
            return None
        
        # Validate and return the rhythm pattern
        return RhythmPattern(**result)
    
    except ValidationError as ve:
        logger.error(f"Validation error fetching rhythm pattern by id {pattern_id}: {ve}")
        return None
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern by id {pattern_id}: {e}")
        return None

async def fetch_note_patterns(
    db: Union[motor.motor_asyncio.AsyncIOMotorDatabase, Any],
    query: Optional[Dict[str, Any]] = None,
) -> List[NotePattern]:
    """
    Fetch note patterns from the database based on an optional query.

    Args:
        db (Union[motor.motor_asyncio.AsyncIOMotorDatabase, Any]): The database connection.
        query (Optional[Dict[str, Any]], optional): Query to filter note patterns. Defaults to None.

    Returns:
        List[NotePattern]: A list of note patterns matching the query.
    """
    try:
        # If query is None, use an empty dictionary
        query = query or {}

        # Fetch note patterns from the database
        if hasattr(db, 'note_patterns'):
            # For MockDatabase, use the mock method
            cursor = db.note_patterns.find(query)
        else:
            # For Motor database, use the standard find method
            cursor = db.note_patterns.find(query)

        # Convert cursor to list, handling both async and sync cursors
        if hasattr(cursor, 'to_list'):
            raw_patterns = await cursor.to_list(length=None)
        elif isinstance(cursor, list):
            raw_patterns = cursor
        elif hasattr(cursor, '__aiter__'):
            # Handle async generator
            raw_patterns = [pattern async for pattern in cursor]
        else:
            # Fallback: try to convert to list
            raw_patterns = list(cursor)

        # Normalize and validate each pattern
        patterns = []
        for pattern_doc in raw_patterns:
            try:
                # Normalize the document
                normalized_doc = _normalize_note_pattern_document(pattern_doc)

                # Ensure pattern is not empty
                if not normalized_doc.get('pattern'):
                    normalized_doc['pattern'] = [0, 2, 4]  # Default pattern

                # Ensure data is a NotePatternData object
                if not isinstance(normalized_doc.get('data'), NotePatternData):
                    normalized_doc['data'] = NotePatternData(
                        notes=[
                            {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                            {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                            {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}
                        ],
                        index=random.randint(1, 10000)
                    )
                elif isinstance(normalized_doc['data'], NotePatternData) and normalized_doc['data'].index is None:
                    normalized_doc['data'].index = random.randint(1, 10000)

                # Generate a random index if not present
                if 'index' not in normalized_doc:
                    normalized_doc['index'] = random.randint(1, 10000)

                # Create NotePattern, handling potential validation errors
                note_pattern = NotePattern(**normalized_doc)
                patterns.append(note_pattern)
            except Exception as pattern_error:
                logger.error(f"Error processing note pattern: {pattern_error}")
                # Create a default pattern with predefined notes
                default_pattern = NotePattern(
                    pattern=[0, 2, 4],
                    index=random.randint(1, 10000),
                    data=NotePatternData(
                        notes=[
                            {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                            {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                            {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}
                        ]
                    )
                )
                patterns.append(default_pattern)

        return patterns

    except Exception as e:
        logger.error(f"Error fetching note patterns: {e}")
        # Return a list with a default pattern
        return [NotePattern(
            pattern=[0, 2, 4],
            index=random.randint(1, 10000),
            data=NotePatternData(
                notes=[
                    {'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                    {'note_name': 'E', 'octave': 4, 'duration': 1.0, 'velocity': 100},
                    {'note_name': 'G', 'octave': 4, 'duration': 1.0, 'velocity': 100}
                ]
            )
        )]

async def fetch_note_pattern_by_id(
    db: Union[motor.motor_asyncio.AsyncIOMotorDatabase, Any], 
    pattern_id: str
) -> Optional[NotePattern]:
    """
    Fetch a specific note pattern by its ID with robust validation.
    
    Args:
        db: MongoDB database connection or MockDatabase
        pattern_id: Unique identifier for the note pattern
    
    Returns:
        Validated NotePattern instance or None if not found
    """
    try:
        if db is None:
            db = await get_db_connection()
        
        # Ensure we're using the correct collection
        note_patterns_collection = db.note_patterns if hasattr(db, 'note_patterns') else db['note_patterns']
        
        # Try multiple ways of matching the ID
        query_conditions = [
            {"id": pattern_id},  # Exact match on 'id' field
            {"_id": pattern_id},  # Match on MongoDB's internal _id 
            {"id": {"$regex": f"^{re.escape(pattern_id)}"}},  # Prefix match
        ]
        
        # Try each query condition
        for condition in query_conditions:
            result = await note_patterns_collection.find_one(condition)
            if result is not None:
                break
        
        # Return None if no pattern found
        if result is None:
            logger.error(f"No note pattern found with ID: {pattern_id}")
            return None
        
        # Normalize the document
        normalized_doc = _normalize_note_pattern_document(result)
        
        # Validate and return the note pattern
        return NotePattern(**normalized_doc)
    
    except ValidationError as ve:
        logger.error(f"Validation error fetching note pattern by id {pattern_id}: {ve}")
        return None
    except Exception as e:
        logger.error(f"Error fetching note pattern by id {pattern_id}: {e}")
        return None

def _get_default_value(field: str) -> Any:
    """
    Get a default value for a given field.
    
    Args:
        field: Name of the field to get a default value for
    
    Returns:
        A default value appropriate for the field
    """
    default_values = {
        'id': str(uuid.uuid4()),
        'name': 'Generated Note Pattern',
        'description': 'Automatically generated note pattern',
        'tags': ['generated'],
        'complexity': 0.5,
        'pattern': [0, 2, 4],
        'data': {
            'notes': [
                {
                    'note_name': 'C', 
                    'octave': 4, 
                    'midi_number': 60, 
                    'duration': 1.0, 
                    'velocity': 64
                }
            ],
            'intervals': [0, 2, 4],
            'duration': 1.0,
            'position': 0.0,
            'velocity': 64,
            'direction': 'forward',
            'use_chord_tones': False,
            'use_scale_mode': False,
            'arpeggio_mode': False,
            'restart_on_chord': False,
            'octave_range': [4, 5],
            'default_duration': 1.0,
            'index': 0
        }
    }
    
    return default_values.get(field, None)

def _normalize_note_pattern_document(
    pattern_doc: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Normalize a note pattern document before validation.

    Args:
        pattern_doc: Raw document from the database

    Returns:
        Normalized document ready for NotePattern validation
    """
    # Create a copy to avoid modifying the original
    normalized_doc = pattern_doc.copy()

    # Ensure required fields exist with default values
    normalized_doc.setdefault('id', str(uuid.uuid4()))
    normalized_doc.setdefault('name', 'Unnamed Pattern')
    normalized_doc.setdefault('pattern', [])
    normalized_doc.setdefault('description', '')

    # Normalize the data field if it exists
    if 'data' in normalized_doc:
        data = normalized_doc['data']
        
        # Convert velocity to float
        if 'velocity' in data:
            data['velocity'] = float(data['velocity'])
        
        # Convert notes' velocities to float
        if 'notes' in data:
            for note in data['notes']:
                if 'velocity' in note:
                    note['velocity'] = float(note['velocity'])
        
        # Convert top-level velocity to float
        if 'velocity' in normalized_doc:
            normalized_doc['velocity'] = float(normalized_doc['velocity'])
        
        normalized_doc['data'] = data

    # Convert data field to NotePatternData if it's a dict
    if 'data' in normalized_doc:
        try:
            # If data is already a NotePatternData instance, keep it
            if isinstance(normalized_doc['data'], NotePatternData):
                return normalized_doc

            # If data is a dictionary, convert it to NotePatternData
            if isinstance(normalized_doc['data'], dict):
                # Ensure velocity is converted to float
                if 'velocity' in normalized_doc['data']:
                    normalized_doc['data']['velocity'] = float(normalized_doc['data']['velocity'])
                
                # Convert notes' velocities to float
                if 'notes' in normalized_doc['data']:
                    for note in normalized_doc['data']['notes']:
                        if 'velocity' in note:
                            note['velocity'] = float(note['velocity'])
                
                normalized_doc['data'] = NotePatternData(**normalized_doc['data'])
            
            # If data is a list or other type, try to create NotePatternData
            elif normalized_doc['data'] is not None:
                normalized_doc['data'] = NotePatternData(notes=normalized_doc['data'])
        except Exception as e:
            logger.warning(f"Could not convert data field to NotePatternData: {e}")
            # Fallback to an empty NotePatternData
            normalized_doc['data'] = NotePatternData()

    return normalized_doc

def _create_default_note_pattern(*args, **kwargs) -> NotePattern:
    """
    Create a default NotePattern instance for error handling.

    Args:
        *args: Ignored positional arguments
        **kwargs: Ignored keyword arguments

    Returns:
        A default NotePattern with minimal valid configuration
    """
    default_pattern_data = {
        'id': str(uuid.uuid4()),
        'name': 'Default Note Pattern',
        'description': 'Automatically generated default note pattern',
        'tags': ['generated', 'default'],
        'complexity': 0.5,
        'notes': [
            {
                'note_name': 'C', 
                'octave': 4, 
                'duration': 1.0, 
                'velocity': 64
            }
        ],
        'data': {
            'notes': [
                {
                    'note_name': 'C', 
                    'octave': 4, 
                    'midi_number': 60, 
                    'duration': 1.0, 
                    'velocity': 64
                }
            ],
            'intervals': [0, 2, 4],
            'duration': 1.0,
            'position': 0.0,
            'velocity': 64,
            'direction': 'forward',
            'use_chord_tones': False,
            'use_scale_mode': False,
            'arpeggio_mode': False,
            'restart_on_chord': False,
            'octave_range': [4, 5],
            'default_duration': 1.0,
            'index': 0
        },
        'is_test': True
    }
    
    try:
        return NotePattern(**default_pattern_data)
    except ValidationError as ve:
        logger.error(f"Error creating default note pattern: {ve}")
        # Fallback to absolute minimal configuration
        return NotePattern(
            id=str(uuid.uuid4()),
            name='Minimal Default Pattern',
            description='Fallback note pattern',
            tags=['generated', 'default', 'minimal'],
            complexity=0.5,
            notes=[],
            data={
                'notes': [],
                'intervals': [0],
                'duration': 1.0,
                'position': 0.0,
                'velocity': 64,
                'direction': 'forward',
                'use_chord_tones': False,
                'use_scale_mode': False,
                'arpeggio_mode': False,
                'restart_on_chord': False,
                'octave_range': [4, 5],
                'default_duration': 1.0,
                'index': 0
            },
            is_test=True
        )

import uuid
from typing import Any, Dict, List, Optional

import motor.motor_asyncio
from pydantic import ValidationError

from src.note_gen.models.note_pattern import NotePattern

# Main execution
if __name__ == "__main__":
    pass