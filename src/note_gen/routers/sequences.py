from fastapi import APIRouter, HTTPException
from src.note_gen.models.note import Note

router = APIRouter()

@router.get("/")
async def get_sequences():
    """Get all available note sequences."""
    try:
        return {"sequences": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_sequence(notes: list[Note]):
    """Create a new note sequence."""
    try:
        return {"sequence_id": "new_sequence"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))