from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_progression import ChordProgression 
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.database import get_db, get_chord_progression_by_name, get_note_pattern_by_name, get_rhythm_pattern_by_name
from src.note_gen.routers.note_sequence_routes import router as note_sequence_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# MongoDB connection


class ChordProgressionRequest(BaseModel):
    scale_info: ScaleInfo = Field(description="Scale information")
    num_chords: int = Field(description="Number of chords")
    progression_pattern: str = Field(description="Progression pattern")

class ChordProgressionResponse(BaseModel):
    id: str = Field(description="ID of the chord progression")
    name: str = Field(description="Name of the chord progression")
    scale_info: Dict[str, Any] = Field(description="Scale information")
    chords: List[Dict[str, Any]] = Field(description="List of chords")

class ApiNotePattern(BaseModel):
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(..., description="Name of the note pattern")
    notes: List[Dict[str, Any]] = Field(..., description="List of notes")
    pattern_type: Optional[str] = Field(None, description="Type of pattern")
    description: str = Field(..., description="Pattern description")
    tags: List[str] = Field(..., description="Pattern tags")
    complexity: Optional[float] = Field(None, description="Pattern complexity")
    data: Optional[Union[NotePatternData, List[int]]] = None



class GenerateSequenceRequest(BaseModel):
    progression_name: str = Field(description="Name of the chord progression preset")
    note_pattern_name: str = Field(description="Name of the note pattern preset")
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
# Existing GET endpoints for chord-progressions
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

@router.post("/generate-sequence", response_model=GenerateSequenceResponse)
async def generate_sequence(request: GenerateSequenceRequest, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> GenerateSequenceResponse:
    """
    Generate a musical sequence based on the provided progression, note pattern, and rhythm pattern.
    """
    logger.debug("Received request: %s", request)
    try:
        logger.info("Request data: %s", request.dict())
        # Fetch chord progression by name
        chord_progression = await get_chord_progression_by_name(request.progression_name, db)
        if not chord_progression:
            raise HTTPException(status_code=404, detail="Chord progression not found")

        # Fetch note pattern by name
        note_pattern = await get_note_pattern_by_name(request.note_pattern_name, db)
        if not note_pattern:
            raise HTTPException(status_code=404, detail="Note pattern not found")

        # Fetch rhythm pattern by name
        rhythm_pattern = await get_rhythm_pattern_by_name(request.rhythm_pattern_name, db)
        if not rhythm_pattern:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")

        # Logic to generate the sequence
        return GenerateSequenceResponse(notes=[], progression_name=request.progression_name, note_pattern_name=request.note_pattern_name, rhythm_pattern_name=request.rhythm_pattern_name)
    except Exception as e:
        logger.error("Error occurred: %s", str(e), exc_info=True)
        logger.error("Request data: %s", request.dict())
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/generate-sequence-new", response_model=GenerateSequenceResponse)
async def generate_sequence_new(request: GenerateSequenceRequest, db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db)) -> GenerateSequenceResponse:
    """
    Generate a musical sequence based on the provided progression, note pattern, and rhythm pattern.
    """
    try:
        # Logic to generate the sequence
        return GenerateSequenceResponse(notes=[], progression_name="", note_pattern_name="", rhythm_pattern_name="")
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

def get_current_user_id():
    # Replace with actual user identification logic
    return "some_user_id"

@router.get("/users/me")
async def get_current_user(db: AsyncIOMotorDatabase = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            logger.warning(f"User not found for ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        logger.error(f"Error retrieving user with ID {user_id}: {e}", exc_info=True)
        logger.error(f"Error details: {e.__dict__}")
        raise HTTPException(status_code=500, detail="Internal Server Error")