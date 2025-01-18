from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Union, Optional, List, Dict, Any 
import logging
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.note_gen.models.musical_elements import Note
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import NotePatternData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# MongoDB connection
from src.note_gen.database import get_db

class Chord(BaseModel):
    root: Dict[str, Any] = Field(description="Root note information")
    quality: str = Field(description="Quality of the chord")

class ChordProgressionRequest(BaseModel):
    scale_info: ScaleInfo = Field(description="Scale information")
    num_chords: int = Field(description="Number of chords")
    progression_pattern: str = Field(description="Progression pattern")

class ChordProgressionResponse(BaseModel):
    id: str = Field(description="ID of the chord progression")
    name: str = Field(description="Name of the chord progression")
    scale_info: Dict[str, Any] = Field(description="Scale information")
    chords: List[Chord] = Field(description="List of chords")

class NotePattern(BaseModel):
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(description="Name of the note pattern")
    notes: List[Dict[str, Any]] = Field(description="List of notes")
    pattern_type: Optional[str] = Field(None, description="Type of pattern")
    description: str = Field(description="Pattern description")
    tags: List[str] = Field(description="Pattern tags")
    complexity: Optional[float] = Field(None, description="Pattern complexity")
    data: Optional[Union[NotePatternData, List[int]]] = None
    # Accept actual Note objects:



class ApiRhythmPatternData(BaseModel):
    notes: List[Dict[str, Any]] = Field(description="List of rhythm notes")
    time_signature: str = Field(description="Time signature")
    swing_enabled: bool = Field(description="Swing enabled flag")
    humanize_amount: float = Field(description="Humanization amount")
    swing_ratio: float = Field(description="Swing ratio")
    default_duration: float = Field(description="Default note duration")
    total_duration: float = Field(description="Total pattern duration")
    accent_pattern: List[float] = Field(description="Accent pattern")
    groove_type: str = Field(description="Groove type")
    variation_probability: float = Field(description="Variation probability")
    duration: float = Field(description="Duration")
    style: str = Field(description="Style")

class ApiRhythmPattern(BaseModel):
    id: Optional[str] = Field(None, description="ID of the rhythm pattern")
    name: str = Field(description="Name of the rhythm pattern")
    description: str = Field(description="Pattern description")
    tags: List[str] = Field(description="Pattern tags")
    complexity: float = Field(description="Pattern complexity")
    style: str = Field(description="Musical style")
    data: ApiRhythmPatternData = Field(description="Rhythm pattern data")

class GenerateSequenceRequest(BaseModel):
    progression_name: str = Field(description="Name of the chord progression preset")
    note_pattern_name: str = Field(description="Name of the note pattern preset")
    rhythm_pattern_name: str = Field(description="Name of the rhythm pattern preset")
    scale_info: ScaleInfo = Field(description="Scale information")

class GeneratedNote(BaseModel):
    note_name: str = Field(description="Name of the note (e.g., C, F#)")
    octave: int = Field(description="Octave number")
    duration: float = Field(description="Duration in beats")
    position: float = Field(description="Position in beats")
    velocity: int = Field(description="Note velocity (0-127)")

class GenerateSequenceResponse(BaseModel):
    notes: List[GeneratedNote] = Field(description="Generated sequence of notes")
    progression_name: str = Field(description="Name of the chord progression used")
    note_pattern_name: str = Field(description="Name of the note pattern used")
    rhythm_pattern_name: str = Field(description="Name of the rhythm pattern used")

def get_next_id() -> str:
    return str(uuid.uuid4())

def get_note_name(midi_number: int) -> str:
    """Get the note name for a given MIDI number."""
    note_name, _ = Note._midi_to_note_octave(midi_number)
    return note_name

def get_octave(midi_number: int) -> int:
    """Get the octave for a given MIDI number."""
    _, octave = Note._midi_to_note_octave(midi_number)
    return octave


# ------------------------------------------------------
# Existing GET endpoints for chord-progressions, note-patterns, rhythm-patterns
# ------------------------------------------------------

@router.get("/chord-progressions", response_model=List[ChordProgressionResponse])
async def list_chord_progressions(
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)
) -> List[ChordProgressionResponse]:
    try:
        cursor = db.chord_progressions.find().skip(skip).limit(limit)
        patterns = await cursor.to_list(length=None)
        return patterns
    except Exception as e:
        logger.error(f"Error listing chord progressions: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/chord-progressions", response_model=List[ChordProgressionResponse])
async def list_chord_progressions(db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)):
    try:
        cursor = db.chord_progressions.find()
        patterns = await cursor.to_list(length=None)
        return patterns
    except Exception as e:
        logger.error(f"Error listing chord progressions: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/note-patterns", response_model=List[NotePattern])
async def get_note_patterns(db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)):
    try:
        cursor = db.note_patterns.find()
        patterns = await cursor.to_list(length=None)
        return patterns
    except Exception as e:
        logger.error(f"Error getting note patterns: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/rhythm-patterns", response_model=List[ApiRhythmPattern])
async def get_rhythm_patterns(db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)):
    try:
        cursor = db.rhythm_patterns.find()
        patterns = await cursor.to_list(length=None)
        return patterns
    except Exception as e:
        logger.error(f"Error getting rhythm patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ------------------------------------------------------
# Existing chord progression create & get by ID
# ------------------------------------------------------

@router.post("/chord-progressions", response_model=ChordProgression)
async def create_chord_progression(
    progression: ChordProgression,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)
) -> ChordProgressionResponse:
    try:
        existing = await db.chord_progressions.find_one({"id": progression.id})
        if existing:
            raise HTTPException(status_code=409, detail="Chord progression with this id already exists")
        
        result = await db.chord_progressions.insert_one(progression.dict())
        if result.inserted_id:
            return ChordProgressionResponse(**progression.dict())
        raise HTTPException(status_code=500, detail="Failed to create chord progression")
    except Exception as e:
        logger.error(f"Error creating chord progression: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/chord-progressions/{progression_id}", response_model=ChordProgressionResponse)
async def get_chord_progression(
    progression_id: str,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)
) -> ChordProgressionResponse:
    try:
        doc = await db.chord_progressions.find_one({"_id": ObjectId(progression_id)})
        if doc is None:
            raise HTTPException(status_code=404, detail="Chord progression not found")
        return ChordProgressionResponse(**doc)
    except Exception as e:
        logger.error(f"Error getting chord progression: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ------------------------------------------------------
# NEW: Create & Get-by-ID for Note Patterns
# ------------------------------------------------------

@router.post("/note-patterns", response_model=NotePattern)
async def create_note_pattern(
    pattern: NotePattern,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)
) -> NotePattern:
    """
    Create a new note pattern in the database.
    """
    try:
        logger.debug(f"Creating note pattern with details: {pattern.dict()}")

        # If no ID was provided, create one
        if pattern.id is None:
            pattern.id = str(ObjectId())

        # Check for duplicate
        logger.debug(f"Checking for existing note pattern with ID: {pattern.id}")
        existing = await db.note_patterns.find_one({"_id": ObjectId(pattern.id)})
        if existing:
            logger.warning(f"Note pattern with id {pattern.id} already exists.")
            raise HTTPException(
                status_code=409, 
                detail=f"Note pattern with id {pattern.id} already exists."
            )
        
        doc = pattern.dict()
        # Move 'id' -> '_id' for Mongo
        doc["_id"] = ObjectId(pattern.id)
        del doc["id"]

        logger.debug(f"Inserting note pattern into database: {doc}")
        result = await db.note_patterns.insert_one(doc)
        if result.inserted_id:
            # Return the same pattern but ensure ID is str
            pattern.id = str(result.inserted_id)
            logger.info(f"Note pattern created successfully with ID: {pattern.id}")
            return pattern
        else:
            logger.error("Failed to create note pattern")
            raise HTTPException(status_code=500, detail="Failed to create note pattern")
    except Exception as e:
        logger.error(f"Error creating note pattern: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/note-patterns/{pattern_id}", response_model=NotePattern)
async def get_note_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)
) -> NotePattern:
    """
    Get a single note pattern by ID.
    """
    try:
        doc = await db.note_patterns.find_one({"_id": ObjectId(pattern_id)})
        if doc is None:
            raise HTTPException(status_code=404, detail="Note pattern not found")
        # Convert back to Pydantic-friendly "id"
        doc["id"] = str(doc.pop("_id"))
        return NotePattern(**doc)
    except Exception as e:
        logger.error(f"Error fetching note pattern: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ------------------------------------------------------
# NEW: Create & Get-by-ID for Rhythm Patterns
# ------------------------------------------------------

@router.post("/rhythm-patterns", response_model=ApiRhythmPattern, status_code=201)
async def create_rhythm_pattern(
    pattern: ApiRhythmPattern,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)
) -> ApiRhythmPattern:
    """
    Create a new rhythm pattern in the database.
    """
    try:
        # If no ID provided, create one
        if pattern.id is None:
            pattern.id = str(ObjectId())

        existing = await db.rhythm_patterns.find_one({"_id": ObjectId(pattern.id)})
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Rhythm pattern with id {pattern.id} already exists."
            )
        
        doc = pattern.dict()
        doc["_id"] = ObjectId(pattern.id)
        del doc["id"]
        
        result = await db.rhythm_patterns.insert_one(doc)
        if result.inserted_id:
            pattern.id = str(result.inserted_id)
            return pattern
        else:
            raise HTTPException(status_code=500, detail="Failed to create rhythm pattern")
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/rhythm-patterns/{pattern_id}", response_model=ApiRhythmPattern)
async def get_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)
) -> ApiRhythmPattern:
    """
    Get a single rhythm pattern by ID.
    """
    try:
        doc = await db.rhythm_patterns.find_one({"_id": ObjectId(pattern_id)})
        if doc is None:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        doc["id"] = str(doc.pop("_id"))
        return ApiRhythmPattern(**doc)
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")