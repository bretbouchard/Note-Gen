from fastapi import APIRouter, HTTPException
from src.note_gen.models.chord import Chord

router = APIRouter()

@router.get("/")
async def get_progressions():
    """Get all available chord progressions."""
    try:
        return {"progressions": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_progression(chords: list[Chord]):
    """Create a new chord progression."""
    try:
        return {"progression_id": "new_progression"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))