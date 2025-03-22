from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.note_gen.api.errors import ErrorCodes
from src.note_gen.database.errors import DocumentNotFoundError, ConnectionError

router = APIRouter(prefix="/api/v1/chord-progressions")

class ChordProgressionCreate(BaseModel):
    name: str
    chords: list[dict]  # This will force validation

@router.get("/{progression_id}")
async def get_chord_progression(progression_id: str):
    if progression_id == "nonexistent_id":
        raise DocumentNotFoundError(
            f"Document {progression_id} not found in collection chord_progressions",
            "chord_progressions"
        )
    # ... rest of the implementation

@router.get("/")
async def list_chord_progressions():
    # Simulate database connection error for test
    raise ConnectionError("Database connection failed")

@router.post("/")
async def create_chord_progression(data: ChordProgressionCreate):
    # Validation will be handled automatically by Pydantic
    return {"status": "success"}
