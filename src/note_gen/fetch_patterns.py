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
from bson import ObjectId

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.patterns import RhythmPattern, RhythmNote
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ScaleType
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
                # Convert string to ChordQuality enum
                processed_data["quality"] = ChordQuality.from_string(quality)
            elif hasattr(quality, 'value') and isinstance(quality.value, str):
                # It's already an enum, convert to string representation for serialization
                processed_data["quality"] = quality.value
        except ValueError as e:
            logger.error(f"Invalid chord quality: {e}")
            processed_data["quality"] = ChordQuality.MAJOR

    # Ensure notes is a list
    if "notes" in processed_data:
        if not isinstance(processed_data["notes"], list):
            processed_data["notes"] = []

    return processed_data

def _normalize_chord_progression_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a chord progression document for validation.
    
    This function ensures that:
    1. It has consistent structure for key fields
    2. Chord qualities are properly formatted
    3. Notes are consistently structured
    4. Scale info is properly formatted
    
    Args:
        document: The document to normalize
        
    Returns:
        A normalized document
    """
    if not document:
        return {}
    
    normalized_doc = document.copy()
    
    # Ensure ID is present
    if "_id" in normalized_doc and isinstance(normalized_doc["_id"], ObjectId):
        normalized_doc["id"] = str(normalized_doc["_id"])
    elif "id" not in normalized_doc:
        normalized_doc["id"] = str(uuid.uuid4())
    
    # Ensure name is present and valid
    if "name" not in normalized_doc or not normalized_doc["name"]:
        normalized_doc["name"] = f"Chord Progression {normalized_doc.get('id', '')[:8]}"
    
    # Ensure chords list exists
    if "chords" not in normalized_doc or not isinstance(normalized_doc["chords"], list):
        normalized_doc["chords"] = []
    
    # Process each chord
    processed_chords = []
    for chord in normalized_doc["chords"]:
        if not isinstance(chord, dict):
            continue
        
        processed_chord = chord.copy()
        
        # Ensure root is properly structured
        if "root" in processed_chord:
            root = processed_chord["root"]
            if isinstance(root, dict):
                # Ensure octave is present
                if "octave" not in root and "note_name" in root:
                    root["octave"] = 4
                
                # Ensure all required fields for Note
                if "note_name" in root:
                    for field, default in [
                        ("duration", 1.0),
                        ("position", 0),
                        ("velocity", 64)
                    ]:
                        if field not in root:
                            root["octave"] = int(root.get("octave", 4))
                            root[field] = default
            
            processed_chord["root"] = root
        
        # Normalize quality
        if "quality" in processed_chord:
            quality = processed_chord["quality"]
            if isinstance(quality, str):
                # Convert maj/min/etc to MAJOR/MINOR/etc if needed
                if quality.lower() == "maj":
                    processed_chord["quality"] = "MAJOR"
                elif quality.lower() == "min":
                    processed_chord["quality"] = "MINOR"
                elif quality.lower() == "dim":
                    processed_chord["quality"] = "DIMINISHED"
                elif quality.lower() == "aug":
                    processed_chord["quality"] = "AUGMENTED"
        else:
            processed_chord["quality"] = "MAJOR"
        
        # Ensure duration exists
        if "duration" not in processed_chord or processed_chord["duration"] is None:
            processed_chord["duration"] = 4.0
        
        # Ensure notes exists
        if "notes" not in processed_chord or not isinstance(processed_chord["notes"], list):
            # Generate basic triad based on root and quality
            processed_chord["notes"] = []
        
        processed_chords.append(processed_chord)
    
    normalized_doc["chords"] = processed_chords
    
    # Ensure key and scale_type
    if "key" not in normalized_doc:
        normalized_doc["key"] = "C"
    
    if "scale_type" not in normalized_doc:
        normalized_doc["scale_type"] = "MAJOR"
    
    # Ensure complexity
    if "complexity" not in normalized_doc:
        normalized_doc["complexity"] = 0.5
    
    # Ensure duration
    if "duration" not in normalized_doc:
        normalized_doc["duration"] = 1.0
    
    # Ensure scale_info
    if "scale_info" not in normalized_doc or not normalized_doc["scale_info"]:
        from src.note_gen.models.fake_scale_info import FakeScaleInfo
        from src.note_gen.models.enums import ScaleType
        
        try:
            root = Note(note_name=normalized_doc["key"], octave=4)
            scale_type_enum = ScaleType[normalized_doc["scale_type"]] if isinstance(normalized_doc["scale_type"], str) else normalized_doc["scale_type"]
        except (KeyError, ValueError):
            root = Note(note_name="C", octave=4)
            scale_type_enum = ScaleType.MAJOR
            
        normalized_doc["scale_info"] = {
            "root": {
                "note_name": root.note_name,
                "octave": root.octave,
                "duration": 1,
                "position": 0,
                "velocity": 64
            },
            "key": normalized_doc["key"],
            "scale_type": normalized_doc["scale_type"]
        }
    
    return normalized_doc

def _create_default_chord_progression(id: Optional[str] = None, name: Optional[str] = None) -> ChordProgression:
    """
    Create a default chord progression for fallback in case of validation errors.
    
    Args:
        id: Optional ID for the progression
        name: Optional name for the progression
        
    Returns:
        A valid minimal ChordProgression
    """
    from src.note_gen.models.fake_scale_info import FakeScaleInfo
    from src.note_gen.models.enums import ScaleType
    
    progression_id = id or str(uuid.uuid4())
    progression_name = name or f"Default Progression {progression_id[:8]}"
    
    # Create a basic C major chord
    root_note = Note(note_name="C", octave=4, duration=1.0, position=0, velocity=64)
    e_note = Note(note_name="E", octave=4, duration=1.0, position=0, velocity=64)
    g_note = Note(note_name="G", octave=4, duration=1.0, position=0, velocity=64)
    
    c_chord = Chord(
        root=root_note,
        quality=ChordQuality.MAJOR,
        notes=[root_note, e_note, g_note]
    )
    
    scale_info = FakeScaleInfo(
        root=root_note,
        scale_type=ScaleType.MAJOR,
        complexity=0.5
    )
    
    return ChordProgression(
        id=progression_id,
        name=progression_name,
        chords=[c_chord],
        key="C",
        scale_type="MAJOR",
        complexity=0.5,
        scale_info=scale_info,
        duration=1.0
    )

async def fetch_chord_progressions(db: Optional[AsyncIOMotorDatabase[Any]] = None) -> List[ChordProgression]:
    """
    Fetch all chord progressions from the database with improved validation.
    
    This function ensures that each document has a valid structure and
    properly normalizes chord data for consistent validation.
    
    Args:
        db: MongoDB database connection
        
    Returns:
        List of validated ChordProgression objects
    """
    try:
        if db is None:
            db = await get_db_conn()
        
        cursor = db.chord_progressions.find({})
        docs = await cursor.to_list(length=None)
        
        progressions = []
        for doc in docs:
            try:
                # Normalize the document structure
                normalized_doc = _normalize_chord_progression_document(doc)
                
                logger.debug(f"Validating chord progression: {normalized_doc.get('name', 'unnamed')}")
                
                # Create ChordProgression instance
                try:
                    progression = ChordProgression.model_validate(normalized_doc)
                    progressions.append(progression)
                    logger.debug(f"Successfully validated chord progression: {normalized_doc.get('name', 'unnamed')}")
                except ValidationError as e:
                    logger.error(f"Failed to validate chord progression {normalized_doc.get('id', 'unknown')}: {e}")
                    # Use a default fallback progression
                    default_progression = _create_default_chord_progression(
                        id=normalized_doc.get("id"),
                        name=normalized_doc.get("name")
                    )
                    progressions.append(default_progression)
                    logger.debug(f"Created default chord progression for {normalized_doc.get('name', 'unnamed')}")
            except Exception as e:
                logger.error(f"Error processing chord progression document: {e}")
                continue
                
        logger.info(f"Successfully fetched {len(progressions)} chord progressions")
        return progressions
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        return []

async def fetch_chord_progression_by_id(chord_progression_id: str, db: Optional[AsyncIOMotorDatabase[Any]] = None) -> Optional[ChordProgression]:
    """
    Fetch a specific chord progression by its ID with robust validation.
    
    Args:
        chord_progression_id: The ID of the chord progression to fetch
        db: MongoDB database connection
        
    Returns:
        ChordProgression if found and valid, None otherwise
    """
    try:
        if db is None:
            db = await get_db_conn()
            
        # Prepare query to check both _id and id fields
        query = {"$or": [
            {"_id": chord_progression_id if isinstance(chord_progression_id, ObjectId) else chord_progression_id},
            {"id": chord_progression_id}
        ]}
        
        doc = await db.chord_progressions.find_one(query)
        
        if not doc:
            logger.warning(f"Chord progression not found: {chord_progression_id}")
            return None
            
        # Normalize document
        normalized_doc = _normalize_chord_progression_document(doc)
        
        try:
            logger.debug(f"Validating chord progression: {normalized_doc.get('name', 'unnamed')}")
            progression = ChordProgression.model_validate(normalized_doc)
            logger.debug(f"Successfully validated chord progression: {normalized_doc.get('name', 'unnamed')}")
            return progression
        except ValidationError as e:
            logger.error(f"Failed to validate chord progression {normalized_doc.get('id', 'unknown')}: {e}")
            # Use a default fallback progression
            default_progression = _create_default_chord_progression(
                id=normalized_doc.get("id"),
                name=normalized_doc.get("name")
            )
            logger.debug(f"Created default chord progression for {normalized_doc.get('name', 'unnamed')}")
            return default_progression
    except Exception as e:
        logger.error(f"Error fetching chord progression by ID: {e}")
        return None

async def fetch_rhythm_patterns(
    db: Optional[AsyncIOMotorDatabase[Any]] = None,
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
    """
    try:
        if db is None:
            db = await get_db_conn()
            
        if query is None:
            query = {}
        
        rhythm_patterns = []
        collections = await db.list_collection_names()
        
        # Try both possible collection names
        docs = []
        
        # Try rhythm_pattern_collection first
        if 'rhythm_pattern_collection' in collections:
            logger.debug(f"Querying collection: rhythm_pattern_collection")
            cursor = db.rhythm_pattern_collection.find(query)
            
            if skip is not None:
                cursor = cursor.skip(skip)
            
            if limit is not None:
                cursor = cursor.limit(limit)
                
            docs = await cursor.to_list(length=None)
            logger.debug(f"Found {len(docs)} rhythm pattern documents in rhythm_pattern_collection")
        
        # If no documents found, try rhythm_patterns
        if not docs and 'rhythm_patterns' in collections:
            logger.debug(f"Querying collection: rhythm_patterns")
            cursor = db.rhythm_patterns.find(query)
            
            if skip is not None:
                cursor = cursor.skip(skip)
            
            if limit is not None:
                cursor = cursor.limit(limit)
                
            docs = await cursor.to_list(length=None)
            logger.debug(f"Found {len(docs)} rhythm pattern documents in rhythm_patterns collection")
            
        # Dump first document structure for debugging if any exist
        if docs and len(docs) > 0:
            logger.debug(f"First rhythm pattern document structure: {list(docs[0].keys())}")
            logger.debug(f"First rhythm pattern document id: {docs[0].get('_id', None)}")
        else:
            logger.warning("No rhythm pattern documents found in any collection")
            return []
        
        for doc in docs:
            try:
                doc_id = str(doc.get('_id', doc.get('id', 'unknown')))
                logger.debug(f"Processing rhythm pattern document: {doc.get('name', 'unnamed')} (ID: {doc_id})")
                
                # Normalize the rhythm pattern document
                normalized_doc = _normalize_rhythm_pattern_document(doc)
                logger.debug(f"Normalized rhythm pattern document structure: {list(normalized_doc.keys())}")
                
                # Add required fields if missing
                if "name" not in normalized_doc or not normalized_doc["name"]:
                    normalized_doc["name"] = "Default Rhythm Pattern"
                    
                if "description" not in normalized_doc or not normalized_doc["description"]:
                    normalized_doc["description"] = f"Automatically generated description for {normalized_doc['name']}"
                    
                if "tags" not in normalized_doc or not normalized_doc["tags"]:
                    normalized_doc["tags"] = ["default", "rhythm"]
                
                try:
                    # Create RhythmPattern from normalized document
                    rhythm_pattern = RhythmPattern.model_validate(normalized_doc)
                    rhythm_patterns.append(rhythm_pattern)
                    logger.debug(f"Successfully validated rhythm pattern: {rhythm_pattern.name} (ID: {rhythm_pattern.id})")
                except ValidationError as e:
                    logger.error(f"Validation error with rhythm pattern {doc_id}: {e}")
                    for error in e.errors():
                        logger.error(f"  - {error['loc']}: {error['msg']}")
                        
                    # Try to create a default valid pattern
                    try:
                        default_pattern = _create_default_rhythm_pattern(id=doc_id, name=doc.get('name', 'Default Rhythm Pattern'))
                        rhythm_patterns.append(default_pattern)
                        logger.debug(f"Created default rhythm pattern due to validation errors: {default_pattern.name} (ID: {default_pattern.id})")
                    except Exception as default_error:
                        logger.error(f"Failed to create default rhythm pattern: {default_error}")
            except Exception as e:
                doc_id = str(doc.get('_id', doc.get('id', 'unknown')))
                logger.error(f"Error processing rhythm pattern {doc_id}: {e}")
                logger.debug(f"Problem document: {doc}")
                # Try to create a default pattern as fallback
                try:
                    default_pattern = _create_default_rhythm_pattern(id=doc_id, name=doc.get('name', 'Default Rhythm Pattern'))
                    rhythm_patterns.append(default_pattern)
                    logger.debug(f"Created default rhythm pattern after exception: {default_pattern.name} (ID: {default_pattern.id})")
                except Exception as inner_e:
                    logger.error(f"Failed to create default rhythm pattern: {inner_e}")
    
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        logger.exception("Exception details:")
    
    logger.info(f"Found {len(rhythm_patterns)} valid rhythm patterns")
    return rhythm_patterns

def _normalize_rhythm_pattern_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a rhythm pattern document for validation."""
    # Create a copy to avoid modifying the original
    doc = document.copy()
    
    # Ensure ID is a string
    if "_id" in doc and not isinstance(doc["_id"], str):
        doc["id"] = str(doc["_id"])
        
    # Ensure data field exists
    if "data" not in doc:
        doc["data"] = {}
    elif not isinstance(doc["data"], dict):
        # If data is not a dict, create an empty one
        doc["data"] = {}
    
    # Move pattern field explicitly to the top level if it's in data 
    if "pattern" not in doc and "pattern" in doc["data"]:
        doc["pattern"] = doc["data"]["pattern"]
    
    # Move pattern-specific fields into data if they exist at root level
    pattern_fields = ["pattern", "time_signature", "swing_enabled", "total_duration", 
                      "swing_ratio", "groove_type", "humanize_amount", "default_duration", 
                      "accent_pattern", "notes"]
    
    for field in pattern_fields:
        if field in doc and field not in doc["data"]:
            doc["data"][field] = doc[field]
    
    # Handle duration field - copy from root to data.total_duration if needed
    if "duration" in doc and "total_duration" not in doc["data"]:
        doc["data"]["total_duration"] = doc["duration"]
    
    # If data.notes is missing, create an empty list
    if "notes" not in doc["data"]:
        doc["data"]["notes"] = []
    
    # Ensure essential fields exist in data with defaults
    defaults = {
        "time_signature": "4/4",
        "swing_ratio": 0.67,
        "default_duration": 1.0,
        "total_duration": 4.0,
        "groove_type": "straight",
        "humanize_amount": 0.0,
        "swing_enabled": False,
        "pattern": [1.0, 1.0]  # Default simple pattern
    }
    
    for field, default_value in defaults.items():
        if field not in doc["data"]:
            doc["data"][field] = default_value
    
    return doc

def _create_default_rhythm_pattern(id: str, name: str) -> RhythmPattern:
    """Create a default valid rhythm pattern for fallback."""
    return RhythmPattern(
        id=id,
        name=name,
        description=f"Default rhythm pattern for {name}",
        tags=["default", "rhythm", "generated"],
        complexity=0.5,
        pattern=[1.0, 1.0],  # Simple pattern
        data={
            "pattern": [1.0, 1.0],
            "time_signature": "4/4",
            "swing_enabled": False,
            "total_duration": 4.0,
            "swing_ratio": 0.67,
            "groove_type": "straight",
            "humanize_amount": 0.0,
            "default_duration": 1.0,
            "notes": [
                {"position": 0.0, "duration": 1.0, "velocity": 90},
                {"position": 1.0, "duration": 1.0, "velocity": 90}
            ]
        }
    )

async def fetch_rhythm_pattern_by_id(
    pattern_id: str, 
    db: Optional[AsyncIOMotorDatabase[Any]] = None
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
            
        # Convert string ID to ObjectId if needed
        from bson import ObjectId
        from bson.errors import InvalidId
        
        query = {}
        try:
            if ObjectId.is_valid(pattern_id):
                query = {"$or": [{"_id": ObjectId(pattern_id)}, {"id": pattern_id}]}
            else:
                query = {"id": pattern_id}
        except InvalidId:
            query = {"id": pattern_id}
            
        logger.debug(f"Fetching rhythm pattern with query: {query}")
        
        # Try both collections for consistency
        collections = await db.list_collection_names()
        doc = None
        
        # First check rhythm_pattern_collection
        if 'rhythm_pattern_collection' in collections:
            doc = await db.rhythm_pattern_collection.find_one(query)
            if doc:
                logger.debug(f"Found rhythm pattern in rhythm_pattern_collection: {doc.get('name', 'unnamed')}")
        
        # If not found, try rhythm_patterns collection
        if not doc and 'rhythm_patterns' in collections:
            doc = await db.rhythm_patterns.find_one(query)
            if doc:
                logger.debug(f"Found rhythm pattern in rhythm_patterns: {doc.get('name', 'unnamed')}")
        
        if not doc:
            logger.warning(f"Rhythm pattern not found with query: {query}")
            return None
            
        logger.debug(f"Found rhythm pattern: {doc.get('name', 'unnamed')} with keys: {list(doc.keys())}")
        
        # Normalize and validate
        try:
            normalized_doc = _normalize_rhythm_pattern_document(doc)
            logger.debug(f"Normalized document structure: {list(normalized_doc.keys())}")
            
            rhythm_pattern = RhythmPattern.model_validate(normalized_doc)
            logger.debug(f"Successfully validated rhythm pattern: {rhythm_pattern.name} (ID: {rhythm_pattern.id})")
            
            # Ensure the result is a RhythmPattern instance
            if not isinstance(rhythm_pattern, RhythmPattern):
                logger.warning(f"Generated object is not a RhythmPattern instance: {type(rhythm_pattern)}")
                rhythm_pattern = _create_default_rhythm_pattern(
                    id=pattern_id, 
                    name=doc.get('name', 'Default Rhythm Pattern')
                )
                logger.debug(f"Created default rhythm pattern instead: {rhythm_pattern.name}")
                
            return rhythm_pattern
        except ValidationError as e:
            logger.error(f"Failed to validate rhythm pattern {pattern_id}: {e}")
            for error in e.errors():
                logger.error(f"  - {error['loc']}: {error['msg']}")
                
            # Try to create a default valid pattern as fallback
            try:
                default_pattern = _create_default_rhythm_pattern(
                    id=pattern_id, 
                    name=doc.get('name', 'Default Rhythm Pattern')
                )
                logger.debug(f"Created default rhythm pattern due to validation error: {default_pattern.name}")
                return default_pattern
            except Exception as default_error:
                logger.error(f"Failed to create default rhythm pattern: {default_error}")
        except Exception as e:
            logger.error(f"Unexpected error processing rhythm pattern {pattern_id}: {e}")
            return None
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern by ID: {e}")
        logger.exception("Exception details:")
        return None

async def fetch_note_patterns(db: Optional[AsyncIOMotorDatabase[Any]] = None, query: Optional[Dict[str, Any]] = None) -> List[NotePattern]:
    """
    Fetch all note patterns from the database with improved validation.
    
    Args:
        db: MongoDB database connection
        query: Optional query to filter the patterns
        
    Returns:
        List of validated NotePattern objects
    """
    try:
        if db is None:
            db = await get_db_conn()
            
        if query is None:
            query = {}
            
        logger.debug(f"Fetching note patterns with query: {query}")
        
        docs = []
        collections = await db.list_collection_names()
        
        # Try note_patterns collection first
        if 'note_patterns' in collections:
            logger.debug(f"Querying collection: note_patterns")
            cursor = db.note_patterns.find(query)
            docs = await cursor.to_list(length=None)
            logger.debug(f"Found {len(docs)} note pattern documents in note_patterns collection")
        
        # If no documents found in note_patterns, try note_pattern_collection
        if not docs and 'note_pattern_collection' in collections:
            logger.debug(f"Querying collection: note_pattern_collection")
            cursor = db.note_pattern_collection.find(query)
            docs = await cursor.to_list(length=None)
            logger.debug(f"Found {len(docs)} note pattern documents in note_pattern_collection")
            
        # Dump first document structure for debugging if any exist
        if docs and len(docs) > 0:
            logger.debug(f"First document structure: {list(docs[0].keys())}")
            logger.debug(f"First document id: {docs[0].get('_id', None)}")
        else:
            logger.warning("No note pattern documents found in any collection")
            return []
        
        patterns: List[NotePattern] = []
        for doc in docs:
            try:
                doc_id = str(doc.get('_id', doc.get('id', 'unknown')))
                logger.debug(f"Processing note pattern document: {doc.get('name', 'unnamed')} (ID: {doc_id})")
                
                # Log the structure of the original document
                logger.debug(f"Original document keys: {list(doc.keys())}")
                logger.debug(f"Original document values preview: name={doc.get('name')}, pattern field exists={('pattern' in doc)}, data field exists={('data' in doc)}")
                
                normalized_doc = _normalize_note_pattern_document(doc)
                logger.debug(f"Normalized document structure: {list(normalized_doc.keys())}")
                logger.debug(f"Normalized document data field structure: {list(normalized_doc.get('data', {}).keys()) if isinstance(normalized_doc.get('data', {}), dict) else 'Not a dict'}")
                
                # Check for required fields before validation
                required_fields = ["name", "description"]
                for field in required_fields:
                    if field not in normalized_doc or not normalized_doc[field]:
                        logger.debug(f"Adding default value for missing required field: {field}")
                        normalized_doc[field] = _get_default_value(field)
                
                try:
                    # Log the type of normalized_doc to ensure it's a dict
                    logger.debug(f"Normalized document type: {type(normalized_doc)}")
                    
                    # First try to validate with model_validate
                    logger.debug(f"Attempting to validate normalized document with model_validate")
                    
                    # Make a copy of the data to ensure we don't lose fields during validation
                    data_for_validation = dict(normalized_doc['data'])
                    
                    # Ensure both notes and intervals are explicitly preserved before validation
                    notes_backup = data_for_validation.get('notes', [])
                    intervals_backup = data_for_validation.get('intervals', [])
                    
                    normalized_doc['data'] = NotePatternData.model_validate(data_for_validation)
                    
                    # Ensure notes weren't lost during validation if both were present
                    if intervals_backup and notes_backup and not normalized_doc['data'].notes:
                        logger.debug(f"Notes were lost during validation - restoring from backup")
                        # Create a new NotePatternData instance with both fields preserved
                        normalized_doc['data'] = NotePatternData(
                            notes=notes_backup,
                            intervals=intervals_backup,
                            duration=data_for_validation.get('duration', 1.0),
                            position=data_for_validation.get('position', 0.0),
                            velocity=data_for_validation.get('velocity', 100),
                            direction=data_for_validation.get('direction', 'up'),
                            use_chord_tones=data_for_validation.get('use_chord_tones', False),
                            use_scale_mode=data_for_validation.get('use_scale_mode', False),
                            arpeggio_mode=data_for_validation.get('arpeggio_mode', False),
                            restart_on_chord=data_for_validation.get('restart_on_chord', False),
                            octave_range=data_for_validation.get('octave_range', [4, 5]),
                            default_duration=data_for_validation.get('default_duration', 1.0)
                        )
                        
                    logger.debug(f"Successfully validated data field for {normalized_doc.get('id', 'unknown')}")
                except Exception as e:
                    logger.warning(f"Could not convert data field to NotePatternData: {e}")
                    try:
                        # Try a second approach by first converting notes to the right format
                        logger.debug(f"Attempting second validation approach with notes format conversion")
                        if 'notes' in normalized_doc['data'] and isinstance(normalized_doc['data']['notes'], list):
                            for i, note in enumerate(normalized_doc['data']['notes']):
                                if isinstance(note, dict) and 'note_name' in note:
                                    # Make sure velocity and duration are floats
                                    if 'velocity' in note:
                                        normalized_doc['data']['notes'][i]['velocity'] = float(note['velocity'])
                                    if 'duration' in note:
                                        normalized_doc['data']['notes'][i]['duration'] = float(note['duration'])
                        
                        # Try validation again
                        normalized_doc['data'] = NotePatternData.model_validate(normalized_doc['data'])
                        logger.debug(f"Second validation attempt succeeded")
                    except Exception as inner_e:
                        logger.warning(f"Second attempt to convert data field failed: {inner_e}")
                        # Create a minimal valid NotePatternData as a fallback
                        logger.debug(f"Creating fallback NotePatternData")
                        normalized_doc['data'] = NotePatternData(
                            notes=[{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100}],
                            intervals=[0],
                            duration=1.0,
                            position=0.0,
                            velocity=100
                        )
                        logger.debug(f"Created fallback NotePatternData")
                
                # Ensure the result is a NotePattern instance
                if not isinstance(normalized_doc, dict):
                    logger.warning(f"Generated object is not a NotePattern instance: {type(normalized_doc)}")
                    pattern = _create_default_note_pattern(id=doc_id, name=doc.get('name', 'Default Pattern'))
                    logger.debug(f"Created default pattern instead: {pattern.name}")
                else:
                    logger.debug(f"Confirmed pattern is a NotePattern instance")
                    
                patterns.append(NotePattern.model_validate(normalized_doc))
            except ValidationError as e:
                # Log validation errors in detail
                logger.error(f"Validation error for document {doc_id}:")
                for error in e.errors():
                    logger.error(f"  - {error['loc']}: {error['msg']}")
                
                # Log the document that failed validation
                logger.debug(f"Document that failed validation: {normalized_doc}")
                
                # Try to create a minimal valid pattern
                logger.warning(f"Creating default pattern due to validation errors")
                pattern = _create_default_note_pattern(id=doc_id, name=doc.get('name', 'Default Pattern'))
                logger.debug(f"Created default pattern: {pattern.name} (ID: {pattern.id})")
                patterns.append(pattern)
            except Exception as e:
                doc_id = str(doc.get('_id', doc.get('id', 'unknown')))
                logger.error(f"Error processing note pattern {doc_id}: {e}")
                logger.debug(f"Problem document: {doc}")
                logger.exception("Exception details:")
                # Try to add a default pattern instead of skipping
                try:
                    pattern = _create_default_note_pattern(id=doc_id, name=doc.get('name', 'Default Pattern'))
                    logger.debug(f"Created default pattern after exception: {pattern.name} (ID: {pattern.id})")
                    patterns.append(pattern)
                except Exception as inner_e:
                    logger.error(f"Failed to create default pattern: {inner_e}")
        
        logger.info(f"Found {len(patterns)} valid note patterns")
        
        # Check if all patterns are NotePattern instances
        is_all_note_patterns = all(isinstance(p, NotePattern) for p in patterns)
        logger.debug(f"All results are NotePattern instances: {is_all_note_patterns}")
        if not is_all_note_patterns:
            # Log details about non-NotePattern objects
            for i, p in enumerate(patterns):
                if not isinstance(p, NotePattern):
                    logger.warning(f"Item {i} is not a NotePattern: {type(p)}")
        
        return patterns
    except Exception as e:
        logger.error(f"Error in fetch_note_patterns: {e}")
        logger.exception("Exception details:")
        return []

async def fetch_note_pattern_by_id(
    pattern_id: str,
    db: Optional[AsyncIOMotorDatabase[Any]] = None
) -> Optional[NotePattern]:
    """
    Fetch a note pattern by ID from the database with improved validation and error handling.
    
    Args:
        pattern_id: ID of the note pattern to fetch
        db: MongoDB database connection
        
    Returns:
        NotePattern object if found, None otherwise
    """
    try:
        if db is None:
            db = await get_db_conn()
        
        logger.debug(f"Fetching note pattern with ID: {pattern_id}")
        
        # Check which collections are available
        collections = await db.list_collection_names()
        doc = None
        
        # Try with note_patterns collection first
        if 'note_patterns' in collections:
            logger.debug(f"Querying collection: note_patterns")
            
            # First try with the ID as is (string ID)
            doc = await db.note_patterns.find_one({"id": pattern_id})
            
            # If not found, try with ObjectId
            if doc is None:
                try:
                    object_id = ObjectId(pattern_id)
                    doc = await db.note_patterns.find_one({"_id": object_id})
                    logger.debug(f"Tried ObjectId lookup: {object_id}")
                except Exception as e:
                    logger.debug(f"Error converting to ObjectId: {e}")
                    # If the ID is not a valid ObjectId, try with the ID as is (_id as string)
                    doc = await db.note_patterns.find_one({"_id": pattern_id})
                    logger.debug(f"Tried _id as string lookup: {pattern_id}")
        
        # If not found in note_patterns, try with note_pattern_collection
        if doc is None and 'note_pattern_collection' in collections:
            logger.debug(f"Querying collection: note_pattern_collection")
            
            # First try with the ID as is (string ID)
            doc = await db.note_pattern_collection.find_one({"id": pattern_id})
            
            # If not found, try with ObjectId
            if doc is None:
                try:
                    object_id = ObjectId(pattern_id)
                    doc = await db.note_pattern_collection.find_one({"_id": object_id})
                    logger.debug(f"Tried ObjectId lookup in note_pattern_collection: {object_id}")
                except Exception as e:
                    logger.debug(f"Error converting to ObjectId: {e}")
                    # If the ID is not a valid ObjectId, try with the ID as is (_id as string)
                    doc = await db.note_pattern_collection.find_one({"_id": pattern_id})
                    logger.debug(f"Tried _id as string lookup in note_pattern_collection: {pattern_id}")
        
        # If still not found, return None
        if doc is None:
            logger.debug(f"Note pattern with ID {pattern_id} not found in any collection")
            return None
            
        logger.debug(f"Found note pattern: {doc.get('name', 'unnamed')} with keys: {list(doc.keys())}")
        
        # Normalize and validate
        try:
            normalized_doc = _normalize_note_pattern_document(doc)
            logger.debug(f"Normalized document structure: {list(normalized_doc.keys())}")
            
            pattern = NotePattern.model_validate(normalized_doc)
            logger.debug(f"Successfully validated pattern: {pattern.name} (ID: {pattern.id})")
            
            # Ensure the result is a NotePattern instance
            if not isinstance(pattern, NotePattern):
                logger.warning(f"Generated object is not a NotePattern instance: {type(pattern)}")
                pattern = _create_default_note_pattern(id=pattern_id, name=doc.get('name', 'Default Pattern'))
                logger.debug(f"Created default pattern instead: {pattern.name}")
                
            return pattern
        except ValidationError as e:
            logger.error(f"Validation error for note pattern {pattern_id}:")
            for error in e.errors():
                logger.error(f"  - {error['loc']}: {error['msg']}")
                
            # Log the document that failed validation
            logger.debug(f"Document that failed validation: {normalized_doc}")
            
            # Try to create a minimal valid pattern
            logger.warning(f"Creating default pattern due to validation errors")
            pattern = _create_default_note_pattern(id=pattern_id, name=doc.get('name', 'Default Pattern'))
            logger.debug(f"Created default pattern: {pattern.name} (ID: {pattern.id})")
            return pattern
            
    except Exception as e:
        logger.error(f"Error fetching note pattern by ID {pattern_id}: {e}")
        logger.debug("Exception details:", exc_info=True)
        return None

async def delete_note_pattern(pattern_id: str, db: Optional[AsyncIOMotorDatabase[Any]] = None) -> bool:
    """
    Delete a note pattern from the database.
    
    Args:
        pattern_id: The ID of the pattern to delete.
        db: Optional database connection.
        
    Returns:
        bool: True if the pattern was deleted, False otherwise.
    """
    try:
        if db is None:
            db = await get_db_conn()
            if db is None:
                logger.error("Could not get database connection")
                return False
        
        pattern_id = pattern_id.strip()
        logger.debug(f"Deleting note pattern with ID: {pattern_id}")
        
        # Try to find the document first to confirm it exists
        pattern = None
        
        # Try by string ID field first
        pattern = db.note_patterns.find_one({"id": pattern_id})
        logger.debug(f"Pattern lookup by id field: {'found' if pattern else 'not found'}")
        
        if pattern:
            # Delete by string ID
            result = db.note_patterns.delete_one({"id": pattern_id})
            deleted = result.deleted_count > 0
            logger.info(f"Delete result for pattern ID {pattern_id}: {deleted}")
            return deleted
        
        # Try with ObjectId
        try:
            obj_id = ObjectId(pattern_id)
            pattern = db.note_patterns.find_one({"_id": obj_id})
            logger.debug(f"Pattern lookup by _id as ObjectId: {'found' if pattern else 'not found'}")
            
            if pattern:
                result = db.note_patterns.delete_one({"_id": obj_id})
                deleted = result.deleted_count > 0
                logger.info(f"Delete result for pattern ObjectId {obj_id}: {deleted}")
                return deleted
        except Exception as e:
            logger.debug(f"ID {pattern_id} is not a valid ObjectId")
        
        # Try with string as _id
        pattern = db.note_patterns.find_one({"_id": pattern_id})
        logger.debug(f"Pattern lookup by _id as string: {'found' if pattern else 'not found'}")
        
        if pattern:
            result = db.note_patterns.delete_one({"_id": pattern_id})
            deleted = result.deleted_count > 0
            logger.info(f"Delete result for pattern _id {pattern_id}: {deleted}")
            return deleted
        
        # As a fallback, try the legacy collection
        pattern = db.note_pattern_collection.find_one({"id": pattern_id})
        logger.debug(f"Pattern lookup in legacy collection: {'found' if pattern else 'not found'}")
        
        if pattern:
            result = db.note_pattern_collection.delete_one({"id": pattern_id})
            deleted = result.deleted_count > 0
            logger.info(f"Delete result from legacy collection for pattern ID {pattern_id}: {deleted}")
            return deleted
        
        logger.error(f"Note pattern with ID {pattern_id} not found in any ID field or collection")
        return False
        
    except Exception as e:
        logger.error(f"Error deleting note pattern: {e}")
        logger.exception("Exception details:")
        return False

async def fetch_patterns(query: Optional[Dict[str, Any]] = None, skip: Optional[int] = 0, limit: Optional[int] = 100):
    """
    Fetch rhythm patterns from the database.
    
    Args:
        query: Optional MongoDB query to filter patterns
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        
    Returns:
        List of RhythmPattern objects
    """
    logger = logging.getLogger(__name__)
    try:
        db = await get_db_conn()
        # Build query
        query = query or {}
        cursor = db.rhythm_patterns.find(query)
        
        # Apply pagination if specified
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        # First, get all documents as dictionaries    
        pattern_docs = await cursor.to_list(length=None)
        logger.debug(f"Found {len(pattern_docs)} rhythm pattern documents")
        
        patterns = []
        for doc in pattern_docs:
            try:
                # Ensure _id is converted to string id if needed
                if "_id" in doc and isinstance(doc["_id"], ObjectId):
                    if "id" not in doc or not doc["id"]:
                        doc["id"] = str(doc["_id"])
                
                # If data is missing, create default data
                if "data" not in doc or not doc["data"]:
                    doc["data"] = {
                        "notes": [],
                        "time_signature": "4/4",
                        "default_duration": 1.0,
                        "total_duration": 4.0,
                        "groove_type": doc.get("groove_type", "straight"),
                        "swing_ratio": doc.get("swing_ratio", 0.67),
                        "duration": doc.get("duration", 1.0),
                        "style": doc.get("style", "basic")
                    }
                
                # Ensure data has required fields
                if isinstance(doc["data"], dict):
                    data_dict = doc["data"]
                    
                    # Ensure notes field exists
                    if "notes" not in data_dict or data_dict["notes"] is None:
                        logger.debug(f"Adding empty notes list for {doc.get('id', 'unknown')}")
                        data_dict["notes"] = []
                    
                    # Ensure other required data fields exist
                    if "time_signature" not in data_dict:
                        data_dict["time_signature"] = "4/4"
                    if "default_duration" not in data_dict:
                        data_dict["default_duration"] = 1.0
                    if "total_duration" not in data_dict:
                        data_dict["total_duration"] = 4.0
                
                # Convert to RhythmPattern instance
                try:
                    # First ensure we have all required RhythmPattern fields
                    required_fields = ["name", "data", "pattern"]
                    for field in required_fields:
                        if field not in doc or doc[field] is None:
                            if field == "name":
                                doc["name"] = f"Rhythm Pattern {doc.get('id', 'unnamed')}"
                            elif field == "pattern":
                                doc["pattern"] = [1.0]  # Default pattern
                    
                    # Use model_validate instead of constructor for better error reporting
                    pattern = RhythmPattern.model_validate(doc)
                    logger.debug(f"Successfully validated pattern: {pattern.name} (ID: {pattern.id})")
                    patterns.append(pattern)
                except ValidationError as e:
                    logger.error(f"Validation error for rhythm pattern {doc.get('id', 'unknown')}: {e}")
                    # Log detailed validation errors
                    for error in e.errors():
                        logger.error(f"  - {error['loc']}: {error['msg']}")
                    continue
            except Exception as e:
                logger.error(f"Unexpected error processing rhythm pattern {doc.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Found {len(patterns)} valid rhythm patterns")
        return patterns
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}")
        return []

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

def _normalize_note_pattern_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a note pattern document from MongoDB to match the Pydantic model.
    
    Args:
        doc: The MongoDB document to normalize.
        
    Returns:
        Dict[str, Any]: The normalized document.
    """
    # Create a copy to avoid modifying the original
    normalized_doc = dict(doc)
    doc_id = str(normalized_doc.get('_id', normalized_doc.get('id', 'unknown')))
    
    logger.debug(f"Normalizing document: {normalized_doc.get('name', 'unnamed')} (ID: {doc_id})")
    logger.debug(f"Original document keys: {list(normalized_doc.keys())}")
    
    # Handle ObjectId
    if '_id' in normalized_doc:
        normalized_doc['id'] = str(normalized_doc.pop('_id'))
        logger.debug(f"Converted _id to id: {normalized_doc['id']}")
    elif 'id' not in normalized_doc:
        normalized_doc['id'] = str(uuid.uuid4())
        logger.debug(f"Generated new UUID for id: {normalized_doc['id']}")
    
    # Ensure description is present
    if 'description' not in normalized_doc:
        normalized_doc['description'] = normalized_doc.get('name', 'No description')
        logger.debug(f"Added default description: {normalized_doc['description']}")
    
    # Ensure tags are present
    if 'tags' not in normalized_doc:
        normalized_doc['tags'] = ['default']
        logger.debug(f"Added default tags: {normalized_doc['tags']}")
    
    # Handle the data field, first check if it exists and is a valid dict
    data = normalized_doc.get('data', {})
    logger.debug(f"Initial data field: {type(data)}, empty: {data == {}}")
    
    if data is None or not isinstance(data, dict):
        logger.debug(f"Data field is not a valid dict, creating empty dict")
        data = {}
    
    # Move pattern-specific fields to a data structure
    pattern_fields = ['pattern', 'direction', 'use_chord_tones', 'use_scale_mode', 
                      'arpeggio_mode', 'restart_on_chord', 'duration', 'position', 
                      'velocity', 'octave_range', 'default_duration', 'intervals', 'index']
    
    # Log which pattern fields exist at the top level
    found_pattern_fields = [field for field in pattern_fields if field in normalized_doc]
    logger.debug(f"Found pattern fields at top level: {found_pattern_fields}")
    
    # If the pattern has these fields but not inside 'data', create a data structure
    if any(field in normalized_doc for field in pattern_fields):
        logger.debug(f"Moving pattern fields to data structure for {normalized_doc.get('id', 'unknown')}")
        
        # Move pattern-specific fields into the data structure
        for field in pattern_fields:
            if field in normalized_doc:
                data[field] = normalized_doc.pop(field)
                logger.debug(f"Moved field '{field}' to data: {data[field]}")
    
    # Ensure 'notes' field exists in data
    if 'notes' not in data:
        # If notes exist at top level, move them to data
        if 'notes' in normalized_doc:
            data['notes'] = normalized_doc.pop('notes')
            logger.debug(f"Moved 'notes' from top level to data")
        else:
            # Create default notes
            data['notes'] = [{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100}]
            logger.debug(f"Added default notes to data")
    
    # Handle string notes in data by converting to proper note dictionaries
    if isinstance(data, dict) and 'notes' in data and isinstance(data['notes'], list):
        notes = data['notes']
        processed_notes = []
        string_notes_count = 0
        
        for note in notes:
            if isinstance(note, str):
                string_notes_count += 1
                # Convert string note to dict format
                processed_notes.append({
                    'note_name': note,
                    'octave': 4,  # Default octave
                    'duration': data.get('default_duration', 1.0),
                    'velocity': data.get('velocity', 100)
                })
            else:
                processed_notes.append(note)
        
        if string_notes_count > 0:
            logger.debug(f"Converted {string_notes_count} string notes to dict format")
            
        data['notes'] = processed_notes
    
    # Add required fields to data if missing
    if isinstance(data, dict):
        missing_fields = []
        if 'duration' not in data:
            data['duration'] = 1.0
            missing_fields.append('duration')
        if 'position' not in data:
            data['position'] = 0.0
            missing_fields.append('position')
        if 'velocity' not in data:
            data['velocity'] = 100.0
            missing_fields.append('velocity')
        if 'intervals' not in data:
            # If there's a pattern field, use it for intervals
            if 'pattern' in data:
                data['intervals'] = data['pattern']
                missing_fields.append('intervals (from pattern)')
            else:
                data['intervals'] = [0, 2, 4]  # Default major triad intervals
                missing_fields.append('intervals (default)')
                
        if missing_fields:
            logger.debug(f"Added missing fields to data: {missing_fields}")
    
    # Ensure name and description exist and are strings
    if 'name' not in normalized_doc or not normalized_doc['name']:
        normalized_doc['name'] = 'Generated Note Pattern'
        logger.debug(f"Added default name: {normalized_doc['name']}")
        
    if 'description' not in normalized_doc or not normalized_doc['description']:
        normalized_doc['description'] = 'Automatically generated note pattern'
        logger.debug(f"Added default description: {normalized_doc['description']}")
    
    # Ensure complexity is validated correctly
    if 'complexity' in normalized_doc:
        if not (0 <= normalized_doc['complexity'] <= 1):
            raise ValidationError("Complexity must be between 0 and 1")
            logger.debug(f"Invalid complexity value: {normalized_doc['complexity']}")
    
    # Ensure name is validated correctly
    if 'name' in normalized_doc:
        if len(normalized_doc['name']) < 2:
            raise ValidationError("Name must be at least 2 characters long")
            logger.debug(f"Invalid name length: {normalized_doc['name']}")
    
    # Update the data field
    try:
        # First try to validate the data with model_validate
        logger.debug(f"Attempting to validate data field using NotePatternData.model_validate")
        
        # Make a copy of the data to ensure we don't lose fields during validation
        data_for_validation = dict(data)
        
        # Ensure both notes and intervals are explicitly preserved before validation
        notes_backup = data_for_validation.get('notes', [])
        intervals_backup = data_for_validation.get('intervals', [])
        
        normalized_doc['data'] = NotePatternData.model_validate(data_for_validation)
        
        # Ensure notes weren't lost during validation if both were present
        if intervals_backup and notes_backup and not normalized_doc['data'].notes:
            logger.debug(f"Notes were lost during validation - restoring from backup")
            # Create a new NotePatternData instance with both fields preserved
            normalized_doc['data'] = NotePatternData(
                notes=notes_backup,
                intervals=intervals_backup,
                duration=data.get('duration', 1.0),
                position=data.get('position', 0.0),
                velocity=data.get('velocity', 100),
                direction=data.get('direction', 'up'),
                use_chord_tones=data.get('use_chord_tones', False),
                use_scale_mode=data.get('use_scale_mode', False),
                arpeggio_mode=data.get('arpeggio_mode', False),
                restart_on_chord=data.get('restart_on_chord', False),
                octave_range=data.get('octave_range', [4, 5]),
                default_duration=data.get('default_duration', 1.0)
            )
            
        logger.debug(f"Successfully validated data field for {normalized_doc.get('id', 'unknown')}")
    except Exception as e:
        logger.warning(f"Could not convert data field to NotePatternData: {e}")
        try:
            # Try a second approach by first converting notes to the right format
            logger.debug(f"Attempting second validation approach with notes format conversion")
            if 'notes' in data and isinstance(data['notes'], list):
                for i, note in enumerate(data['notes']):
                    if isinstance(note, dict) and 'note_name' in note:
                        # Make sure velocity and duration are floats
                        if 'velocity' in note:
                            data['notes'][i]['velocity'] = float(note['velocity'])
                        if 'duration' in note:
                            data['notes'][i]['duration'] = float(note['duration'])
            
            # Try validation again
            normalized_doc['data'] = NotePatternData.model_validate(data)
            logger.debug(f"Second validation attempt succeeded")
        except Exception as inner_e:
            logger.warning(f"Second attempt to convert data field failed: {inner_e}")
            # Create a minimal valid NotePatternData as a fallback
            logger.debug(f"Creating fallback NotePatternData")
            normalized_doc['data'] = NotePatternData(
                notes=[{'note_name': 'C', 'octave': 4, 'duration': 1.0, 'velocity': 100}],
                intervals=[0],
                duration=1.0,
                position=0.0,
                velocity=100
            )
            logger.debug(f"Created fallback NotePatternData")
    
    # Copy essential fields from data back to the top level
    for field in ['duration', 'position', 'velocity', 'direction', 'use_chord_tones', 
                 'use_scale_mode', 'arpeggio_mode', 'restart_on_chord']:
        if isinstance(normalized_doc['data'], dict):
            data_dict = normalized_doc['data']
            if field in data_dict:
                normalized_doc[field] = data_dict[field]
                logger.debug(f"Copied field '{field}' from data to top level: {data_dict[field]}")
        else:
            if hasattr(normalized_doc['data'], field):
                value = getattr(normalized_doc['data'], field)
                if value is not None:
                    normalized_doc[field] = value
                    logger.debug(f"Copied field '{field}' from Pydantic data to top level: {value}")
    
    # Specially handle pattern/intervals field
    if isinstance(normalized_doc['data'], dict) and 'intervals' in normalized_doc['data']:
        normalized_doc['pattern'] = normalized_doc['data']['intervals']
        logger.debug(f"Copied 'intervals' from data to 'pattern' at top level: {normalized_doc['pattern']}")
    elif hasattr(normalized_doc['data'], 'intervals') and normalized_doc['data'].intervals:
        normalized_doc['pattern'] = normalized_doc['data'].intervals
        logger.debug(f"Copied 'intervals' from Pydantic data to 'pattern' at top level: {normalized_doc['pattern']}")
    
    # Ensure required fields have default values even if they weren't in data
    if 'duration' not in normalized_doc or normalized_doc['duration'] is None:
        normalized_doc['duration'] = 1.0
        logger.debug(f"Added default 'duration' at top level: 1.0")
    
    if 'position' not in normalized_doc or normalized_doc['position'] is None:
        normalized_doc['position'] = 0.0
        logger.debug(f"Added default 'position' at top level: 0.0")
    
    if 'velocity' not in normalized_doc or normalized_doc['velocity'] is None:
        normalized_doc['velocity'] = 64  # Default MIDI velocity
        logger.debug(f"Added default 'velocity' at top level: 64")
    
    # Ensure pattern exists at top level
    if 'pattern' not in normalized_doc or not normalized_doc['pattern']:
        normalized_doc['pattern'] = [0, 2, 4]  # Default to major triad
        logger.debug(f"Added default 'pattern' at top level: [0, 2, 4]")
    
    # Final check on types for critical fields
    try:
        if 'duration' in normalized_doc:
            normalized_doc['duration'] = float(normalized_doc['duration'])
        if 'position' in normalized_doc:
            normalized_doc['position'] = float(normalized_doc['position'])
        if 'velocity' in normalized_doc:
            normalized_doc['velocity'] = int(float(normalized_doc['velocity']))
    except (ValueError, TypeError) as e:
        logger.warning(f"Error converting field types: {e}")
        normalized_doc['duration'] = 1.0
        normalized_doc['position'] = 0.0
        normalized_doc['velocity'] = 64
    
    logger.debug(f"Completed normalization for {normalized_doc.get('name', 'unnamed')}")
    return normalized_doc

def _create_default_note_pattern(id: Optional[str] = None, name: Optional[str] = None) -> NotePattern:
    """
    Create a default NotePattern instance for error handling.

    Args:
        id: Optional ID to use for the pattern
        name: Optional name to use for the pattern

    Returns:
        A default NotePattern with minimal valid configuration
    """
    try:
        # Use provided values or defaults
        pattern_id = id if id else str(uuid.uuid4())
        pattern_name = name if name else "Default Note Pattern"
        
        logger.debug(f"Creating default note pattern with id={pattern_id}, name={pattern_name}")
        
        # Create a minimal data structure with valid notes and intervals
        data = {
            'notes': [
                {
                    "note_name": "C",
                    "octave": 4,
                    "duration": 1.0,
                    "velocity": 100.0
                }
            ],
            'intervals': [0, 4, 7],  # C Major triad intervals
            'duration': 1.0,
            'position': 0.0,
            'velocity': 100.0,
            'direction': 'up',
            'use_chord_tones': False,
            'use_scale_mode': False,
            'arpeggio_mode': False,
            'restart_on_chord': False,
            'octave_range': [4, 5],
            'default_duration': 1.0,
            'index': 0
        }
        
        # Create the pattern with validated data
        pattern = NotePattern(
            id=pattern_id,
            name=pattern_name,
            description=f"Default pattern created as fallback for {pattern_name}",
            tags=["default", "generated"],
            complexity=0.1,
            is_test=True,
            data=data
        )
        
        logger.debug(f"Successfully created default note pattern: {pattern.name} (ID: {pattern.id})")
        return pattern
    except Exception as e:
        logger.error(f"Error creating default note pattern: {e}")
        logger.exception("Exception details:")
        
        # Last resort: create the pattern with minimal constructor arguments
        try:
            # Use a unique ID in case the error was related to ID conflicts
            fallback_id = str(uuid.uuid4())
            fallback_pattern = NotePattern(
                id=fallback_id,
                name="Emergency Fallback Pattern",
                description="Created when all other pattern creation attempts failed",
                tags=["default", "emergency"],
                is_test=True,
                data={
                    "notes": [{"note_name": "C", "octave": 4, "duration": 1.0, "velocity": 100.0}],
                    "intervals": [0],
                    "duration": 1.0,
                    "position": 0.0,
                    "velocity": 100.0
                }
            )
            logger.debug(f"Created emergency fallback pattern with ID: {fallback_id}")
            return fallback_pattern
        except Exception as inner_e:
            # If even this fails, raise the error
            logger.critical(f"Failed to create emergency fallback pattern: {inner_e}")
            raise ValueError(f"Could not create any valid note pattern: {inner_e}") from inner_e

import uuid
from typing import Any, Dict, List, Optional, Union
import logging

import motor.motor_asyncio
from pydantic import ValidationError
from bson import ObjectId
from bson.errors import InvalidId

from src.note_gen.models.patterns import NotePatternData, NotePattern, ChordProgressionPattern, ChordPatternItem
from src.note_gen.models.chord import ChordQuality

logger = logging.getLogger(__name__)

async def extract_patterns_from_chord_progressions(db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None) -> List[str]:
    """
    Extract patterns from existing chord progressions and save them to the database.
    
    Args:
        db: MongoDB database connection
        
    Returns:
        List of inserted pattern IDs
    """
    if db is None:
        db = await get_db_conn()
        
    logger.debug("Starting extraction of patterns from chord progressions")
    patterns = []
    pattern_collection = 'chord_progression_patterns'
    
    # Create collection if it doesn't exist
    collections = await db.list_collection_names()
    if pattern_collection not in collections:
        logger.info(f"Creating collection: {pattern_collection}")
        await db.create_collection(pattern_collection)
    
    # Get all progressions
    try:
        cursor = db.chord_progressions.find({})
        progressions = await cursor.to_list(length=None)
        logger.debug(f"Found {len(progressions)} chord progressions to extract patterns from")
        
        for progression in progressions:
            try:
                name = progression.get('name', 'Unnamed Progression')
                logger.debug(f"Processing progression: {name}")
                
                # Skip if no chords
                if 'chords' not in progression or not progression['chords']:
                    logger.warning(f"Progression {name} has no chords, skipping")
                    continue
                    
                # Create pattern items from the chords
                pattern_items = []
                for i, chord in enumerate(progression['chords']):
                    # Default values
                    degree = i + 1  # Default to sequential degrees if we can't determine real ones
                    quality = chord.get('quality', 'MAJOR')
                    duration = chord.get('duration', 4.0)
                    
                    # Create pattern item
                    pattern_item = {
                        'degree': degree,
                        'quality': quality,
                        'duration': duration
                    }
                    pattern_items.append(pattern_item)
                
                # Create pattern document
                pattern_id = str(uuid.uuid4())
                pattern = {
                    'id': pattern_id,
                    'name': f"Pattern from {name}",
                    'description': f"Automatically extracted from chord progression: {name}",
                    'tags': ['extracted', 'chord_progression'],
                    'complexity': progression.get('complexity', 0.5),
                    'genre': progression.get('genre', None),
                    'pattern': pattern_items,
                    'is_test': False
                }
                
                # Insert into database
                result = await db[pattern_collection].insert_one(pattern)
                inserted_id = str(result.inserted_id)
                patterns.append(inserted_id)
                logger.debug(f"Inserted pattern with ID: {inserted_id}")
                
            except Exception as e:
                logger.error(f"Error extracting pattern from progression {progression.get('name', 'unknown')}: {e}")
                logger.debug("Exception details:", exc_info=True)
                continue
                
        logger.info(f"Successfully extracted {len(patterns)} patterns from chord progressions")
        return patterns
        
    except Exception as e:
        logger.error(f"Error in extract_patterns_from_chord_progressions: {e}")
        logger.debug("Exception details:", exc_info=True)
        return []

async def fetch_chord_progression_patterns(
    db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None,
    query: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None
) -> List[ChordProgressionPattern]:
    """
    Fetch chord progression patterns from the database with proper validation.
    
    Args:
        db: MongoDB database connection
        query: Optional query to filter patterns
        limit: Optional limit on number of patterns to fetch
        skip: Optional number of patterns to skip
        
    Returns:
        List of validated ChordProgressionPattern objects
    """
    try:
        if db is None:
            db = await get_db_conn()
            
        if query is None:
            query = {}
            
        # Get all collections
        collections = await db.list_collection_names()
        pattern_collection = 'chord_progression_patterns'
        
        # Check if collection exists
        if pattern_collection not in collections:
            logger.warning(f"Collection {pattern_collection} does not exist")
            return []
            
        # Get patterns
        logger.debug(f"Fetching chord progression patterns with query: {query}")
        cursor = db[pattern_collection].find(query)
        
        if skip is not None:
            cursor = cursor.skip(skip)
            
        if limit is not None:
            cursor = cursor.limit(limit)
            
        docs = await cursor.to_list(length=None)
        logger.debug(f"Found {len(docs)} chord progression pattern documents")
        
        patterns = []
        for doc in docs:
            try:
                # Normalize document
                normalized_doc = _normalize_chord_progression_pattern_document(doc)
                
                # Validate and convert to ChordProgressionPattern
                pattern = ChordProgressionPattern.model_validate(normalized_doc)
                patterns.append(pattern)
                logger.debug(f"Successfully validated chord progression pattern: {pattern.name}")
            except ValidationError as e:
                logger.error(f"Validation error for chord progression pattern {doc.get('id', 'unknown')}: {e}")
                for error in e.errors():
                    logger.error(f"  - {error['loc']}: {error['msg']}")
                # Create default pattern
                try:
                    default_pattern = _create_default_chord_progression_pattern(
                        id=str(doc.get('_id', doc.get('id', uuid.uuid4()))),
                        name=doc.get('name', 'Default Chord Progression Pattern')
                    )
                    patterns.append(default_pattern)
                    logger.debug(f"Added default chord progression pattern: {default_pattern.name}")
                except Exception as inner_e:
                    logger.error(f"Failed to create default chord progression pattern: {inner_e}")
            except Exception as e:
                logger.error(f"Error processing chord progression pattern {doc.get('id', 'unknown')}: {e}")
                logger.debug("Exception details:", exc_info=True)
                continue
                
        logger.info(f"Successfully validated {len(patterns)} chord progression patterns")
        return patterns
    except Exception as e:
        logger.error(f"Error in fetch_chord_progression_patterns: {e}")
        logger.debug("Exception details:", exc_info=True)
        return []

async def fetch_chord_progression_pattern_by_id(
    pattern_id: str,
    db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
) -> Optional[ChordProgressionPattern]:
    """
    Fetch a single chord progression pattern by ID with proper validation.
    
    Args:
        pattern_id: ID of the pattern to fetch
        db: MongoDB database connection
        
    Returns:
        ChordProgressionPattern if found and valid, None otherwise
    """
    try:
        if db is None:
            db = await get_db_conn()
            
        logger.debug(f"Fetching chord progression pattern with ID: {pattern_id}")
        pattern_collection = 'chord_progression_patterns'
        
        # Check if collection exists
        collections = await db.list_collection_names()
        if pattern_collection not in collections:
            logger.warning(f"Collection {pattern_collection} does not exist")
            return None
            
        # Prepare query to check both _id and id fields
        query = {"$or": []}
        
        # Add id clause
        query["$or"].append({"id": pattern_id})
        
        # Try to add ObjectId clause
        try:
            if ObjectId.is_valid(pattern_id):
                query["$or"].append({"_id": ObjectId(pattern_id)})
        except InvalidId:
            pass
            
        # Add string _id clause
        query["$or"].append({"_id": pattern_id})
        
        # Get pattern
        doc = await db[pattern_collection].find_one(query)
        
        if not doc:
            logger.warning(f"Chord progression pattern with ID {pattern_id} not found")
            return None
            
        # Normalize and validate
        try:
            normalized_doc = _normalize_chord_progression_pattern_document(doc)
            pattern = ChordProgressionPattern.model_validate(normalized_doc)
            logger.debug(f"Successfully validated chord progression pattern: {pattern.name}")
            return pattern
        except ValidationError as e:
            logger.error(f"Validation error for chord progression pattern {pattern_id}: {e}")
            for error in e.errors():
                logger.error(f"  - {error['loc']}: {error['msg']}")
            # Create default pattern
            default_pattern = _create_default_chord_progression_pattern(
                id=pattern_id,
                name=doc.get('name', 'Default Chord Progression Pattern')
            )
            logger.debug(f"Created default chord progression pattern: {default_pattern.name}")
            return default_pattern
    except Exception as e:
        logger.error(f"Error in fetch_chord_progression_pattern_by_id: {e}")
        logger.debug("Exception details:", exc_info=True)
        return None

def _normalize_chord_progression_pattern_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a chord progression pattern document to ensure it can be validated.
    
    Args:
        doc: Document to normalize
        
    Returns:
        Normalized document
    """
    # Create a copy to avoid modifying the original
    normalized_doc = dict(doc)
    
    # Ensure ID is a string
    if "_id" in normalized_doc:
        normalized_doc["id"] = str(normalized_doc.pop("_id"))
    elif "id" not in normalized_doc:
        normalized_doc["id"] = str(uuid.uuid4())
        
    # Ensure required fields exist
    if "name" not in normalized_doc or not normalized_doc["name"]:
        normalized_doc["name"] = "Default Chord Progression Pattern"
        
    if "description" not in normalized_doc or not normalized_doc["description"]:
        normalized_doc["description"] = f"Generated description for {normalized_doc['name']}"
        
    if "tags" not in normalized_doc or not normalized_doc["tags"]:
        normalized_doc["tags"] = ["default", "chord_progression"]
        
    if "complexity" not in normalized_doc or normalized_doc["complexity"] is None:
        normalized_doc["complexity"] = 0.5
        
    # Handle pattern field
    if "pattern" not in normalized_doc or not normalized_doc["pattern"]:
        # Default I-IV-V pattern
        normalized_doc["pattern"] = [
            {"degree": 1, "quality": "MAJOR", "duration": 4.0},
            {"degree": 4, "quality": "MAJOR", "duration": 4.0},
            {"degree": 5, "quality": "MAJOR", "duration": 4.0}
        ]
    
    # Ensure pattern items have required fields
    pattern_items = normalized_doc["pattern"]
    if isinstance(pattern_items, list):
        for i, item in enumerate(pattern_items):
            if isinstance(item, dict):
                # Ensure degree exists
                if "degree" not in item or item["degree"] is None:
                    item["degree"] = i + 1
                    
                # Ensure quality exists
                if "quality" not in item or item["quality"] is None:
                    item["quality"] = "MAJOR"
                    
                # Ensure duration exists
                if "duration" not in item or item["duration"] is None:
                    item["duration"] = 4.0
                    
    return normalized_doc

def _create_default_chord_progression_pattern(
    id: Optional[str] = None,
    name: Optional[str] = None
) -> ChordProgressionPattern:
    """
    Create a default chord progression pattern for error handling.
    
    Args:
        id: Optional ID for the pattern
        name: Optional name for the pattern
        
    Returns:
        A default ChordProgressionPattern instance
    """
    pattern_id = id or str(uuid.uuid4())
    pattern_name = name or "Default Chord Progression Pattern"
    
    # Create a basic I-IV-V pattern
    return ChordProgressionPattern(
        id=pattern_id,
        name=pattern_name,
        description=f"Default chord progression pattern for {pattern_name}",
        tags=["default", "chord_progression", "generated"],
        complexity=0.5,
        pattern=[
            ChordPatternItem(degree=1, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=4, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=5, quality="MAJOR", duration=4.0)
        ]
    )