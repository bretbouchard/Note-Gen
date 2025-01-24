from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Union, Optional, List, Dict, Any 
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.note_gen.models.musical_elements import Note
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternResponse
from src.note_gen.models.note_pattern import NotePatternResponse

from src.note_gen.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# MongoDB connection


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

class ApiNotePattern(BaseModel):
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(..., description="Name of the note pattern")
    notes: List[Dict[str, Any]] = Field(..., description="List of notes")
    pattern_type: Optional[str] = Field(None, description="Type of pattern")
    description: str = Field(..., description="Pattern description")
    tags: List[str] = Field(..., description="Pattern tags")
    complexity: Optional[float] = Field(None, description="Pattern complexity")
    data: Optional[Union[NotePatternData, List[int]]] = None



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
    return str(ObjectId())

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
async def get_chord_progressions(db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> List[ChordProgressionResponse]:
    logger.info("Database instance type: %s", type(db))
    try:
        logger.info("Fetching chord progressions from the database.")
        cursor = await db.chord_progressions.find()  # Fetch the cursor
        progressions = await cursor.to_list(length=100)  # Specify length to get the data
        logger.info("Fetched chord progressions: %s", progressions)
        return [ChordProgressionResponse(id=str(p["_id"]), **{k: v for k, v in p.items() if k != "_id"}) for p in progressions]
    except Exception as e:
        logger.error(f"Error getting chord progressions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/note-patterns", response_model=List[NotePattern])
async def get_note_patterns(db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> List[NotePattern]:
    """
    Retrieve all note patterns from the database.
    """
    try:
        cursor: AsyncIOMotorCursor[Dict[str, Any]] = db.note_patterns.find()
        note_patterns = await cursor.to_list(length=100)
        return note_patterns
    except Exception as e:
        logger.error(f"Error getting note patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
        

@router.get("/rhythm-patterns", response_model=List[RhythmPattern])
async def get_rhythm_patterns(db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> List[RhythmPattern]:
    """
    Retrieve all rhythm patterns from the database.
    """
    try:
        cursor = db.rhythm_patterns.find()
        rhythm_patterns = await cursor.to_list(length=100)
        return rhythm_patterns
    except Exception as e:
        logger.error(f"Error getting rhythm patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
# ------------------------------------------------------
# Existing chord progression create & get by ID
# ------------------------------------------------------

@router.post("/chord-progressions", response_model=ChordProgressionResponse)
async def create_chord_progression(progression: ChordProgression, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> ChordProgressionResponse:
    try:
        logger.debug(f"Creating chord progression with details: {progression.dict()}")
        
        # Convert the progression to dict and handle ObjectId
        progression_dict = progression.dict()
        logger.debug(f"Progression data to be inserted: {progression_dict}")
        logger.debug(f"Inserting chord progression into database: {progression_dict}")
        # Insert progression into the database
        result = await db['chord_progressions'].insert_one(progression_dict)
        logger.debug(f"Inserted chord progression into database with result: {result}")

        # Create response with string ID
        response_dict = progression_dict.copy()
        response_dict['id'] = str(result.inserted_id)  # Ensure ObjectId is serialized
        logger.info(f"Chord progression created with ID: {response_dict['id']} and data: {response_dict}")
        logger.debug(f"Serialized response: {response_dict}")
        return ChordProgressionResponse(**response_dict)
    except Exception as e:
        logger.error(f"Error creating chord progression: {e}", exc_info=True)
        logger.error(f"Error details: {e.__dict__}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/chord-progressions/{progression_id}", response_model=ChordProgressionResponse)
async def get_chord_progression(progression_id: str, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> ChordProgressionResponse:
    try:
        # Convert string ID to ObjectId
        try:
            object_id = ObjectId(progression_id)
            logger.debug(f"Converting progression_id to ObjectId: {progression_id}")
        except Exception as e:
            logger.error(f"Invalid ObjectId format: {progression_id}. Error: {e}")
            logger.error(f"Error details: {e.__dict__}")
            raise HTTPException(status_code=400, detail="Invalid ID format")

        doc = await db['chord_progressions'].find_one({"_id": object_id})
        logger.debug(f"Retrieved document from database: {doc}")
        if doc is None:
            logger.warning(f"Chord progression not found for ID: {progression_id}")
            logger.error(f"Error details: Chord progression not found for ID: {progression_id}")
            raise HTTPException(status_code=404, detail="Chord progression not found")
        
        # Convert _id to string id for response
        if doc:
            doc['_id'] = str(doc['_id'])
        return ChordProgressionResponse(**doc)
    except Exception as e:
        logger.error(f"Error retrieving chord progression: {e}", exc_info=True)
        logger.error(f"Error details: {e.__dict__}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# ------------------------------------------------------
# NEW: Create & Get-by-ID for Note Patterns
# ------------------------------------------------------

@router.post("/note-patterns", response_model=NotePattern)
async def create_note_pattern(note_pattern: NotePattern, db: AsyncIOMotorDatabase = Depends(get_db)) -> NotePattern:
    """
    Create a new note pattern
    """
    note_pattern_data = jsonable_encoder(note_pattern)
    logger.debug(f'Note pattern data before insertion: {note_pattern_data}')
    try:
        # Ensure db is accessed correctly
        result = await db.note_patterns.insert_one(note_pattern_data)
        if result is None:
            raise HTTPException(status_code=500, detail='Database insertion failed')
        created_note_pattern = await db.note_patterns.find_one({'_id': result.inserted_id})
        return created_note_pattern
    except Exception as e:
        logger.error(f'Error creating note pattern: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')

@router.get("/note-patterns/{pattern_id}", response_model=NotePattern)
async def get_note_pattern(pattern_id: str, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> NotePattern:
    """
    Get a single note pattern by ID.
    """
    try:
        object_id = ObjectId(pattern_id)
        note_pattern = await db.note_patterns.find_one({"_id": object_id})
        if note_pattern is None:
            raise HTTPException(status_code=404, detail="Note pattern not found")
        return note_pattern
    except Exception as e:
        logger.error(f"Error fetching note pattern: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ------------------------------------------------------
# NEW: Create & Get-by-ID for Rhythm Patterns
# ------------------------------------------------------

@router.post("/rhythm-patterns", response_model=ApiRhythmPattern, status_code=201)
async def create_rhythm_pattern(pattern: ApiRhythmPattern, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> ApiRhythmPattern:
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
        
        logger.debug(f"Inserting rhythm pattern into database: {doc}")
        result = await db.rhythm_patterns.insert_one(doc)
        if result.inserted_id:
            pattern.id = str(result.inserted_id)
            logger.info(f"Rhythm pattern created successfully with ID: {pattern.id}")
            logger.debug(f"Serialized response: {pattern.dict()}")
            return pattern
        else:
            raise HTTPException(status_code=500, detail="Failed to create rhythm pattern")
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}", exc_info=True)
        logger.error(f"Error details: {e.__dict__}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/rhythm-patterns/{pattern_id}", response_model=ApiRhythmPattern)
async def get_rhythm_pattern(pattern_id: str, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> ApiRhythmPattern:
    """
    Get a single rhythm pattern by ID.
    """
    try:
        object_id = ObjectId(pattern_id)
        rhythm_pattern = await db.rhythm_patterns.find_one({"_id": object_id})
        if rhythm_pattern is None:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        return rhythm_pattern
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/generate-chord-progression", response_model=List[ChordProgressionResponse])
async def generate_chord_progression(request: Request, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> List[ChordProgressionResponse]:
    logger.info("Database instance type: %s", type(db))
    data = await request.json()
    logger.info(f"Received data: {data}")
    cursor = await db.chord_progressions.find()
    progressions = await cursor.to_list(length=100)
    logger.info("Fetched chord progressions: %s", progressions)
    return [ChordProgressionResponse(id=str(p["_id"]), **p) for p in progressions]

@router.post("/generate-sequence", response_model=GenerateSequenceResponse)
async def generate_sequence(request: GenerateSequenceRequest, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> GenerateSequenceResponse:
    """
    Generate a musical sequence based on the provided progression, note pattern, and rhythm pattern.
    """
    try:
        # Logic to generate the sequence
        return {"message": "Sequence generated successfully"}
    except Exception as e:
        logger.error(f"Error generating sequence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/generate-sequence-new", response_model=GenerateSequenceResponse)
async def generate_sequence_new(request: GenerateSequenceRequest, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> GenerateSequenceResponse:
    """
    Generate a musical sequence based on the provided progression, note pattern, and rhythm pattern.
    """
    try:
        # Logic to generate the sequence
        return {"message": "New sequence generated successfully"}
    except Exception as e:
        logger.error(f"Error generating new sequence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/test-db", response_model=Dict[str, Any])
async def test_db_connection(db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> Dict[str, Any]:
    try:
        chord_progression = await db.chord_progressions.find_one()
        if chord_progression:
            return chord_progression
        else:
            return {"message": "No chord progressions found."}
    except Exception as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")