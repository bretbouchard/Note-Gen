"""
Routes for chord progression operations.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(
    prefix="/api/v1",
    tags=["chord-progressions"]
)

@router.post("/chord-progressions", response_model=ChordProgression)
async def create_chord_progression(
    progression: ChordProgression,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> ChordProgression:
    """Create a new chord progression."""
    try:
        # Convert to dict for MongoDB storage
        prog_dict = progression.dict()
        # Store in database
        result = await db.chord_progressions.insert_one(prog_dict)
        # Add the generated ID to the progression
        progression.id = str(result.inserted_id)
        return progression
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/chord-progressions", response_model=List[ChordProgression])
async def get_chord_progressions(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[ChordProgression]:
    """Get all chord progressions."""
    try:
        cursor = db.chord_progressions.find()
        progressions = await cursor.to_list(length=None)
        return [ChordProgression(**prog) for prog in progressions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
