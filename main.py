from fastapi import FastAPI, HTTPException      
from pydantic import BaseModel  
from typing import List, Optional
from src.note_gen.routers.user_routes import router as user_router
from src.note_gen.import_presets import ensure_indexes, import_presets_if_empty
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ScaleDegree(BaseModel):
    degree: int
    note: str

class ChordProgressionRequest(BaseModel):
    style: str = "basic"
    start_degree: Optional[int] = None

class ScaleInfo(BaseModel):
    root: str
    scale: str

class ChordProgressionGenerator(BaseModel):
    """Generator for chord progressions."""
    progression: List[ScaleDegree] = []  # Default to an empty list
    scale_info: ScaleInfo

    def generate_progression(self, style: str = "basic", start_degree: Optional[int] = None) -> List[ScaleDegree]:
        """Generate a chord progression."""
        # This is a placeholder implementation
        return self.progression

    def parse_progression(self, progression_str: str) -> List[str]:
        """Parse a chord progression string."""
        # This is a placeholder implementation
        return progression_str.split()

    def generate_notes_from_chord(self, progression: List[str]) -> List[str]:
        """Generate notes from a chord progression."""
        # This is a placeholder implementation
        return progression

# Rebuild the model to ensure dependencies are recognized
# ChordProgressionGenerator.model_rebuild()

app = FastAPI()  # <-- The main app
app.include_router(user_router, prefix="", tags=["User Routes"])

# Initialize your generators
root_note = 'C'  # Example root note
scale = 'major'  # Example scale type
scale_info = ScaleInfo(root=root_note, scale=scale)
chord_generator = ChordProgressionGenerator(scale_info=scale_info)

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database with presets on startup."""

    client: AsyncIOMotorClient[Any] = AsyncIOMotorClient('mongodb://localhost:27017/')

    db: AsyncIOMotorDatabase[Any] = client['note_gen']  # Replace with your database name
    await ensure_indexes(db) 
    await import_presets_if_empty(db) 

@app.post("/generate_progression/")
async def generate_progression(request: ChordProgressionRequest) -> List[ScaleDegree]:
    try:
        return chord_generator.generate_progression(
            style=request.style,
            start_degree=request.start_degree
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate_note_sequence/")
async def generate_note_sequence(chord_progression: str) -> List[str]:
    """Generate a note sequence based on a given chord progression."""
    try:
        progression = chord_generator.parse_progression(chord_progression)
        note_sequence = chord_generator.generate_notes_from_chord(progression)
        return note_sequence
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/progression/{progression_id}")
async def get_progression(progression_id: int) -> dict[str, str | int]:
    """Retrieve a specific chord progression by ID."""
    # Logic to retrieve the progression based on ID (implement as needed)
    return {"progression_id": progression_id, "progression": "example"}

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Chord Progression Generator API!"}

# Add more endpoints as needed
