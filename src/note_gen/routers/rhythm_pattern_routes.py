# src/note_gen/routers/rhythm_pattern_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from motor import motor_asyncio
from src.note_gen.dependencies import get_db
from src.note_gen.models.rhythm_pattern import RhythmPattern
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Create a new rhythm pattern
@router.post("/rhythm-patterns", response_model=RhythmPattern)
async def create_rhythm_pattern(pattern: RhythmPattern, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    try:
        logger.info(f"Creating rhythm pattern: {pattern}")
        result = await db.rhythm_patterns.insert_one(pattern.dict())
        pattern.id = str(result.inserted_id)
        logger.info(f"Rhythm pattern created with ID: {pattern.id}")
        return pattern
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get a single rhythm pattern by ID
@router.get("/rhythm-patterns/{pattern_id}")
async def get_rhythm_pattern(pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Fetching rhythm pattern with ID: {pattern_id}")
    pattern = await db.rhythm_patterns.find_one({"_id": ObjectId(pattern_id)})
    if pattern is None:
        logger.warning(f"Rhythm pattern not found for ID: {pattern_id}")
        raise HTTPException(status_code=404, detail="Rhythm pattern not found")
    return pattern

# Get all rhythm patterns
@router.get("/rhythm-patterns", response_model=List[RhythmPattern])
async def get_rhythm_patterns(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Fetching all rhythm patterns")
    patterns = await db.rhythm_patterns.find().to_list(length=None)
    return patterns
