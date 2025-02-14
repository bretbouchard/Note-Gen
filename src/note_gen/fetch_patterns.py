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
from src.note_gen.database.db import get_db_conn
from src.note_gen.dependencies import get_db_conn

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
    if not isinstance(chord_data, dict):
        raise ValueError(f"Expected chord_data to be a dictionary, got {type(chord_data)}")

    processed_data = chord_data.copy()

    # Handle root note
    if "root" in processed_data:
        root_data = processed_data["root"]
        if isinstance(root_data, dict):
            try:
                if "note_name" in root_data and "octave" in root_data:
                    processed_data["root"] = Note(
                        note_name=root_data["note_name"],
                        octave=root_data["octave"]
                    )
            except ValidationError as e:
                logger.error(f"Failed to create Note instance: {e}")
                raise ValueError(f"Invalid root note data: {root_data}")

    # Handle quality
    if "quality" in processed_data:
        try:
            quality = processed_data["quality"]
            if isinstance(quality, str):
                processed_data["quality"] = ChordQualityType(quality.upper())
        except ValueError as e:
            logger.error(f"Invalid chord quality: {e}")
            processed_data["quality"] = ChordQualityType.MAJOR

    # Ensure notes is a list
    if "notes" in processed_data:
        if not isinstance(processed_data["notes"], list):
            processed_data["notes"] = []

    return processed_data

async def fetch_chord_progressions(db: Optional[AsyncIOMotorDatabase] = None) -> List[ChordProgression]:
    """Fetch all chord progressions from the database."""
    try:
        if db is None:
            db = await get_db_conn()
        cursor = db.chord_progressions.find({})
        progressions = []
        async for doc in cursor:
            try:
                # Process each chord in the progression
                if "chords" in doc:
                    doc["chords"] = [process_chord_data(chord) for chord in doc["chords"]]
                
                # Create ChordProgression instance
                progression = ChordProgression(**doc)
                progressions.append(progression)
            except ValidationError as e:
                logger.error(f"Failed to validate chord progression: {e}")
                continue
        return progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def fetch_chord_progression_by_id(chord_progression_id: str, db: Optional[AsyncIOMotorDatabase] = None) -> Optional[ChordProgression]:
    """Fetch a specific chord progression by its ID."""
    try:
        if db is None:
            db = await get_db_conn()
        doc = await db.chord_progressions.find_one({"_id": chord_progression_id})
        if doc:
            # Process each chord in the progression
            if "chords" in doc:
                doc["chords"] = [process_chord_data(chord) for chord in doc["chords"]]
            return ChordProgression(**doc)
        return None
    except Exception as e:
        logger.error(f"Error fetching chord progression by ID: {e}")
        return None

async def fetch_rhythm_patterns(
    db: Optional[AsyncIOMotorDatabase] = None,
    query: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None
) -> List[RhythmPattern]:
    """
    Fetch rhythm patterns from the database with improved error handling.
    
    Args:
        db: The MongoDB database connection.
        query: Optional query to filter rhythm patterns
        limit: Optional limit on number of patterns to fetch
        skip: Optional number of patterns to skip
    
    Returns:
        List[RhythmPattern]: A list of validated rhythm patterns.
    
    Raises:
        ValueError: If a rhythm pattern fails validation.
    """
    try:
        if db is None:
            db = await get_db_conn()
        # Build query
        query = query or {}
        cursor = db.rhythm_patterns.find(query)
        
        # Apply pagination if specified
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
            
        patterns = []
        async for doc in cursor:
            try:
                # Convert to RhythmPattern instance
                pattern = RhythmPattern(**doc)
                patterns.append(pattern)
            except ValidationError as e:
                logger.error(f"Failed to validate rhythm pattern {doc.get('id', 'unknown')}: {e}")
                continue
                
        return patterns
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

async def fetch_rhythm_pattern_by_id(
    pattern_id: str, 
    db: Optional[AsyncIOMotorDatabase] = None
) -> Optional[RhythmPattern]:
    """
    Fetch a specific rhythm pattern by its ID with comprehensive validation.
    
    Args:
        pattern_id: The unique identifier of the rhythm pattern.
        db: MongoDB database connection
    
    Returns:
        A validated rhythm pattern or None if not found or invalid.
    """
    try:
        if db is None:
            db = await get_db_conn()
        doc = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if not doc:
            return None
        
        try:
            return RhythmPattern(**doc)
        except ValidationError as e:
            logger.error(f"Failed to validate rhythm pattern {pattern_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing rhythm pattern {pattern_id}: {e}")
            return None
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern by ID: {e}")
        return None

async def fetch_note_patterns(
    db: Optional[AsyncIOMotorDatabase] = None,
    query: Optional[Dict[str, Any]] = None,
) -> List[NotePattern]:
    """
    Fetch note patterns from the database based on an optional query.

    Args:
        db: The database connection.
        query: Query to filter note patterns. Defaults to None.

    Returns:
        List[NotePattern]: A list of note patterns matching the query.
    """
    try:
        if db is None:
            db = await get_db_conn()

        # Build query
        query = query or {}
        cursor = db.note_patterns.find(query)
        patterns = []
        
        async for doc in cursor:
            try:
                # Normalize document before validation
                normalized_doc = _normalize_note_pattern_document(doc)
                
                # Create NotePattern instance
                pattern = NotePattern(**normalized_doc)
                patterns.append(pattern)
            except ValidationError as e:
                logger.error(f"Failed to validate note pattern {doc.get('id', 'unknown')}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing note pattern {doc.get('id', 'unknown')}: {e}")
                continue
                
        return patterns
    except Exception as e:
        logger.error(f"Error fetching note patterns: {e}")
        return []

async def fetch_note_pattern_by_id(
    pattern_id: str,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Optional[NotePattern]:
    """
    Fetch a specific note pattern by its ID with robust validation.
    
    Args:
        pattern_id: Unique identifier for the note pattern
        db: MongoDB database connection
    
    Returns:
        Validated NotePattern instance or None if not found
    """
    try:
        if db is None:
            db = await get_db_conn()
        doc = await db.note_patterns.find_one({"_id": pattern_id})
        if not doc:
            return None
        
        try:
            normalized_doc = _normalize_note_pattern_document(doc)
            return NotePattern(**normalized_doc)
        except ValidationError as e:
            logger.error(f"Failed to validate note pattern {pattern_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing note pattern {pattern_id}: {e}")
            return None
    except Exception as e:
        logger.error(f"Error fetching note pattern by ID: {e}")
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
    except ValidationError as e:
        logger.error(f"Error creating default note pattern: {e}")
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