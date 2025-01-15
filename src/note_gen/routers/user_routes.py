from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Generator
import logging
import uuid
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

from src.note_gen.models.musical_elements import Note
from src.note_gen.models.scale import Scale, ScaleType
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.note_sequence_generator import NoteSequenceGenerator
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote
from src.note_gen.models.presets import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS
from note_gen.models.scale_info import ScaleInfo

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Note Generation API", version="1.0.0")

# Initialize router
router = APIRouter()

# MongoDB connection
client: AsyncIOMotorClient[Any] = AsyncIOMotorClient('mongodb://localhost:27017/')

db = client.note_gen

async def get_db() -> AsyncIOMotorDatabase[Any]:
    """Get database connection."""
    try:
        await client.admin.command('ping')
        return db
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

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
    chords: List[str] = Field(description="List of chords")
    key: str = Field(description="Key of the progression")
    scale_type: str = Field(description="Scale type of the progression")
    complexity: float = Field(description="Complexity of the progression")

class NotePattern(BaseModel):
    id: str = Field(description="ID of the note pattern")
    name: str = Field(description="Name of the note pattern")
    notes: List[Dict[str, Any]] = Field(description="List of notes")
    pattern_type: str = Field(description="Type of pattern")
    description: str = Field(description="Pattern description")
    tags: List[str] = Field(description="Pattern tags")
    complexity: float = Field(description="Pattern complexity")

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
    id: str = Field(description="ID of the rhythm pattern")
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

def convert_to_api_rhythm_pattern_data(rhythm_pattern_data: RhythmPatternData) -> ApiRhythmPatternData:
    return ApiRhythmPatternData(
        notes=[note.dict() for note in rhythm_pattern_data.notes],
        time_signature=rhythm_pattern_data.time_signature,
        swing_enabled=rhythm_pattern_data.swing_enabled,
        humanize_amount=rhythm_pattern_data.humanize_amount,
        swing_ratio=rhythm_pattern_data.swing_ratio,
        style=rhythm_pattern_data.style,
        default_duration=rhythm_pattern_data.default_duration,
        total_duration=rhythm_pattern_data.total_duration,
        accent_pattern=rhythm_pattern_data.accent_pattern,
        groove_type=rhythm_pattern_data.groove_type,
        variation_probability=rhythm_pattern_data.variation_probability,
        duration=rhythm_pattern_data.duration,
    )

def get_note_name(midi_number: int) -> str:
    """Convert MIDI number to note name."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_name = notes[midi_number % 12]
    return note_name  # Return just the note name without octave

def get_octave(midi_number: int) -> int:
    return midi_number // 12 - 1  # Calculate the octave

def get_next_id() -> str:
    return str(uuid.uuid4())

@router.post("/chord-progressions", response_model=ChordProgressionResponse)
async def create_chord_progression(
    progression: ChordProgression, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> ChordProgressionResponse:
    try:
        # Check if progression with same id already exists
        existing = await db.chord_progressions.find_one({"id": progression.id})
        if existing:
            raise HTTPException(status_code=409, detail="Chord progression with this id already exists")
        
        # Create new progression
        result = await db.chord_progressions.insert_one(progression.model_dump())
        if result.inserted_id:
            return ChordProgressionResponse(**progression.model_dump())
        raise HTTPException(status_code=500, detail="Failed to create chord progression")
    except Exception as e:
        logger.error(f"Error creating chord progression: {e}")
        raise HTTPException(status_code=500, detail="Error creating chord progression")

@router.get("/chord-progressions/{progression_id}", response_model=ChordProgressionResponse)
async def get_chord_progression(
    progression_id: str,
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> ChordProgressionResponse:
    try:
        progression = await db.chord_progressions.find_one({"id": progression_id})
        if progression is None:
            raise HTTPException(status_code=404, detail="Chord progression not found")
        return ChordProgressionResponse(**progression)
    except Exception as e:
        logger.error(f"Error getting chord progression: {e}")
        raise HTTPException(status_code=500, detail="Error getting chord progression")

@router.put("/chord-progressions/{progression_id}", response_model=ChordProgressionResponse)
async def update_chord_progression(
    progression_id: str,
    progression: ChordProgression,
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> ChordProgressionResponse:
    try:
        # Update progression
        result = await db.chord_progressions.update_one(
            {"id": progression_id},
            {"$set": progression.model_dump()}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Chord progression not found")
        return ChordProgressionResponse(**progression.model_dump())
    except Exception as e:
        logger.error(f"Error updating chord progression: {e}")
        raise HTTPException(status_code=500, detail="Error updating chord progression")

@router.delete("/chord-progressions/{progression_id}")
async def delete_chord_progression(
    progression_id: str, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> dict[str, str]:
    try:
        result = await db.chord_progressions.delete_one({"id": progression_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chord progression not found")
        return {"message": "Chord progression deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting chord progression: {e}")
        raise HTTPException(status_code=500, detail="Error deleting chord progression")

@router.get("/chord-progressions", response_model=List[ChordProgressionResponse])
async def list_chord_progressions(
    skip: int = 0, 
    limit: int = 10, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> List[ChordProgressionResponse]:
    try:
        cursor = db.chord_progressions.find().skip(skip).limit(limit)
        progressions = []
        async for doc in cursor:
            progressions.append(ChordProgressionResponse(**doc))
        return progressions
    except Exception as e:
        logger.error(f"Error listing chord progressions: {e}")
        raise HTTPException(status_code=500, detail="Error listing chord progressions")

@router.get("/note-patterns", response_model=List[NotePattern])
async def get_note_patterns(
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> List[NotePattern]:
    try:
        cursor = db.note_patterns.find()
        patterns = []
        async for doc in cursor:
            patterns.append(NotePattern(**doc))
        return patterns
    except Exception as e:
        logger.error(f"Error getting note patterns: {e}")
        raise HTTPException(status_code=500, detail="Error getting note patterns")

@router.get("/note-patterns/{id}", response_model=NotePattern)
async def get_note_pattern_by_id(
    id: str, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> NotePattern:
    try:
        pattern = await db.note_patterns.find_one({"id": id})
        if pattern is None:
            raise HTTPException(status_code=404, detail="Note pattern not found")
        return NotePattern(**pattern)
    except Exception as e:
        logger.error(f"Error getting note pattern: {e}")
        raise HTTPException(status_code=500, detail="Error getting note pattern")

@router.post("/note-patterns", response_model=NotePattern)
async def create_note_pattern(
    pattern: NotePattern, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> NotePattern:
    try:
        result = await db.note_patterns.insert_one(pattern.model_dump())
        if result.inserted_id:
            return pattern
        raise HTTPException(status_code=500, detail="Failed to create note pattern")
    except Exception as e:
        logger.error(f"Error creating note pattern: {e}")
        raise HTTPException(status_code=500, detail="Error creating note pattern")

@router.delete("/note-patterns/{pattern_id}")
async def delete_note_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> dict[str, str]:
    try:
        result = await db.note_patterns.delete_one({"id": pattern_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note pattern not found")
        return {"message": "Note pattern deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting note pattern: {e}")
        raise HTTPException(status_code=500, detail="Error deleting note pattern")

@router.get("/rhythm-patterns", response_model=List[ApiRhythmPattern])
async def get_rhythm_patterns(
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> List[ApiRhythmPattern]:
    try:
        cursor = db.rhythm_patterns.find()
        patterns = []
        async for doc in cursor:
            patterns.append(ApiRhythmPattern(**doc))
        return patterns
    except Exception as e:
        logger.error(f"Error getting rhythm patterns: {e}")
        raise HTTPException(status_code=500, detail="Error getting rhythm patterns")

@router.get("/rhythm-patterns/{id}", response_model=ApiRhythmPattern)
async def get_rhythm_pattern_by_id(
    id: str, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> ApiRhythmPattern:
    try:
        pattern = await db.rhythm_patterns.find_one({"_id": ObjectId(id)})
        if pattern is None:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        return ApiRhythmPattern(**pattern)
    except Exception as e:
        logger.error(f"Error getting rhythm pattern: {e}")
        raise HTTPException(status_code=500, detail="Error getting rhythm pattern")

@router.post("/rhythm-patterns", response_model=ApiRhythmPattern)
async def create_rhythm_pattern(
    rhythm_pattern: ApiRhythmPattern, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> ApiRhythmPattern:
    try:
        result = await db.rhythm_patterns.insert_one(rhythm_pattern.model_dump())
        if result.inserted_id:
            return rhythm_pattern
        raise HTTPException(status_code=500, detail="Failed to create rhythm pattern")
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}")
        raise HTTPException(status_code=500, detail="Error creating rhythm pattern")

@router.delete("/rhythm-patterns/{pattern_id}")
async def delete_rhythm_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> dict[str, str]:
    try:
        result = await db.rhythm_patterns.delete_one({"_id": ObjectId(pattern_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        return {"message": "Rhythm pattern deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern: {e}")
        raise HTTPException(status_code=500, detail="Error deleting rhythm pattern")

@router.post("/generate-chord-progression", response_model=ChordProgressionResponse)
async def generate_chord_progression(
    request: ChordProgressionRequest, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> ChordProgressionResponse:
    try:
        # Generate progression based on request
        progression_id = str(ObjectId())
        progression = ChordProgressionResponse(
            id=progression_id,
            name=f"Generated Progression {progression_id[:8]}",
            chords=["C", "Am", "F", "G"],  # Example chords
            key=request.scale_info.root_note,
            scale_type=request.scale_info.scale_type,
            complexity=0.5
        )
        return progression
    except Exception as e:
        logger.error(f"Error generating chord progression: {e}")
        raise HTTPException(status_code=500, detail="Error generating chord progression")

@router.post("/generate-sequence", response_model=GenerateSequenceResponse)
async def generate_sequence(
    request: GenerateSequenceRequest, 
    db: AsyncIOMotorDatabase[Any] = Depends(get_db)
) -> GenerateSequenceResponse:
    try:
        # Generate sequence based on request
        notes = [
            GeneratedNote(
                note_name="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=100
            ),
            GeneratedNote(
                note_name="E",
                octave=4,
                duration=1.0,
                position=1.0,
                velocity=100
            ),
            GeneratedNote(
                note_name="G",
                octave=4,
                duration=1.0,
                position=2.0,
                velocity=100
            )
        ]
        return GenerateSequenceResponse(
            notes=notes,
            progression_name=request.progression_name,
            note_pattern_name=request.note_pattern_name,
            rhythm_pattern_name=request.rhythm_pattern_name
        )
    except Exception as e:
        logger.error(f"Error generating sequence: {e}")
        raise HTTPException(status_code=500, detail="Error generating sequence")

app.include_router(router)
