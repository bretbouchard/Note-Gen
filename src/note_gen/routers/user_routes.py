from fastapi import FastAPI, APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Generator
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

def get_db() -> Generator[Database[Any], None, None]:
    """Get database connection."""
    try:
        client: MongoClient[Any] = MongoClient('mongodb://localhost:27017/')
        db = client.note_gen
        yield db
    finally:
        client.close()

# MongoDB connection

class ScaleInfo(BaseModel):
    root: Dict[str, Any] = Field(description="Root note information")
    scale_type: str = Field(description="Type of scale")

class Chord(BaseModel):
    root: Dict[str, Any] = Field(description="Root note information")
    quality: str = Field(description="Quality of the chord")

class ChordProgressionRequest(BaseModel):
    scale_info: ScaleInfo = Field(description="Scale information")
    chords: List[Chord] = Field(description="List of chords")
    root: Optional[Dict[str, Any]] = Field(None, description="Optional root note")

class ChordProgressionResponse(BaseModel):
    id: str = Field(description="ID of the chord progression")
    name: str = Field(description="Name of the chord progression")
    chords: List[Dict[str, Any]] = Field(description="List of chords")

class NotePattern(BaseModel):
    id: str = Field(description="ID of the note pattern")
    name: str = Field(description="Name of the note pattern")
    pattern: List[int] = Field(description="Note pattern data")

class RhythmPattern(BaseModel):
    id: str = Field(description="ID of the rhythm pattern")
    name: str = Field(description="Name of the rhythm pattern")
    pattern: Dict[str, Any] = Field(description="Rhythm pattern data")

@router.get("/chord-progressions", response_model=List[ChordProgressionResponse])
async def get_chord_progressions(db: Database[Any] = Depends(get_db)) -> List[ChordProgressionResponse]:
    try:
        progressions = list(db.chord_progressions.find({}, {'_id': 0}))
        if not progressions:
            # Return default progression if none found
            return [ChordProgressionResponse(
                id=str(uuid.uuid4()),
                name="I-IV-V",
                chords=[
                    {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
                    {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
                    {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
                ]
            )]
        return [ChordProgressionResponse(**prog) for prog in progressions]
    except Exception as e:
        logger.error(f"Error fetching chord progressions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching chord progressions")

@router.get("/chord-progressions/{id}", response_model=ChordProgressionResponse)
async def get_chord_progression_by_id(id: str, db: Database[Any] = Depends(get_db)) -> ChordProgressionResponse:
    try:
        progression = db.chord_progressions.find_one({'id': id}, {'_id': 0})
        if not progression:
            raise HTTPException(status_code=404, detail="Chord progression not found")
        return ChordProgressionResponse(**progression)
    except Exception as e:
        logger.error(f"Error fetching chord progression by ID: {e}")
        raise HTTPException(status_code=500, detail="Error fetching chord progression")

@router.get("/note-patterns", response_model=List[NotePattern])
async def get_note_patterns(db: Database[Any] = Depends(get_db)) -> List[NotePattern]:
    patterns = list(db.note_patterns.find({}, {'_id': 0}))
    return [NotePattern(**pattern) for pattern in patterns]

@router.get("/note-patterns/{id}", response_model=NotePattern)
async def get_note_pattern_by_id(id: str, db: Database[Any] = Depends(get_db)) -> NotePattern:
    try:
        pattern = db.note_patterns.find_one({'id': id}, {'_id': 0})
        if not pattern:
            raise HTTPException(status_code=404, detail="Note pattern not found")
        return NotePattern(**pattern)
    except Exception as e:
        logger.error(f"Error fetching note pattern by ID: {e}")
        raise HTTPException(status_code=500, detail="Error fetching note pattern")

@router.get("/rhythm-patterns", response_model=List[RhythmPattern])
async def get_rhythm_patterns(db: Database[Any] = Depends(get_db)) -> List[RhythmPattern]:
    patterns = list(db.rhythm_patterns.find({}, {'_id': 0}))
    return [RhythmPattern(**pattern) for pattern in patterns]

@router.get("/rhythm-patterns/{id}", response_model=RhythmPattern)
async def get_rhythm_pattern_by_id(id: str, db: Database[Any] = Depends(get_db)) -> RhythmPattern:
    try:
        pattern = db.rhythm_patterns.find_one({'id': id}, {'_id': 0})
        if not pattern:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        return RhythmPattern(**pattern)
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern by ID: {e}")
        raise HTTPException(status_code=500, detail="Error fetching rhythm pattern")

@router.post("/generate_progression", response_model=ChordProgressionResponse)
async def generate_progression(request: ChordProgressionRequest, db: Database[Any] = Depends(get_db)) -> ChordProgressionResponse:
    # Process the chord progression
    chords = [{"root": chord.root, "quality": chord.quality} for chord in request.chords]
    progression_id = str(uuid.uuid4())
    db.chord_progressions.insert_one({
        "id": progression_id,
        "name": "Generated Progression",
        "chords": chords
    })
    return ChordProgressionResponse(
        id=progression_id,
        name="Generated Progression",
        chords=chords
    )

app.include_router(router)
