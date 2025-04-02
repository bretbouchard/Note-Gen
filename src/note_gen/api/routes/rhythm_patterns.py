from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class RhythmNoteCheck(BaseModel):
    position: float
    duration: float
    velocity: int
    is_rest: Optional[bool] = False

class RhythmPatternCheck(BaseModel):
    notes: List[RhythmNoteCheck]
    time_signature: str

@router.post("/")
async def create_rhythm_pattern(pattern: RhythmPatternCheck):
    """Create a new rhythm pattern."""
    try:
        # Validate time signature format
        num, denom = map(int, pattern.time_signature.split('/'))
        if denom not in [2, 4, 8, 16]:
            return {"is_valid": False, "error": "Invalid time signature denominator"}

        # Validate note positions are in order
        positions = [note.position for note in pattern.notes]
        if positions != sorted(positions):
            return {"is_valid": False, "error": "Notes must be in chronological order"}

        # Return success response
        return {"is_valid": True}

    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid pattern format")

@router.post("/check")
async def check_rhythm_pattern(pattern: RhythmPatternCheck):
    """Check if a rhythm pattern is valid."""
    try:
        # Validate time signature format
        num, denom = map(int, pattern.time_signature.split('/'))
        if denom not in [2, 4, 8, 16]:
            return {"is_valid": False, "error": "Invalid time signature denominator"}

        # Validate note positions are in order
        positions = [note.position for note in pattern.notes]
        if positions != sorted(positions):
            return {"is_valid": False, "error": "Notes must be in chronological order"}

        # Return the validated pattern data
        return {
            "is_valid": True,
            "pattern": pattern.model_dump()  # Changed from .dict() to .model_dump()
        }

    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid pattern format")

@router.get("/{pattern_id}")
async def get_rhythm_pattern(pattern_id: str):
    """Get a rhythm pattern by ID."""
    # Your pattern retrieval logic
    return {"pattern": "pattern data"}
