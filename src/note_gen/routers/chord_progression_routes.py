"""
Consolidated routes for chord progression operations with improved error handling and logging.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.patterns import ChordProgression
from ..database.db import get_db_conn
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(
    prefix="/api/v1/chord-progressions",
    tags=["chord-progressions"]
)

@router.get("/", response_model=List[ChordProgression])
async def get_chord_progressions(db: AsyncIOMotorDatabase = Depends(get_db_conn)):
    """Get all chord progressions"""
    cursor = db.chord_progressions.find({})
    chord_progressions = await cursor.to_list(length=None)
    return [ChordProgression(**cp) for cp in chord_progressions]

@router.post("/create", response_model=ChordProgression, status_code=201)
async def create_chord_progression(
    chord_progression: ChordProgression,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """Create a new chord progression"""
    result = await db.chord_progressions.insert_one(chord_progression.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=400, detail="Failed to create chord progression")
    
    created_progression = await db.chord_progressions.find_one({"_id": result.inserted_id})
    return ChordProgression(**created_progression)
