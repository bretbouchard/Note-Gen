# src/note_gen/routers/note_pattern_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from motor import motor_asyncio
from src.note_gen.dependencies import get_db
from src.note_gen.models.note_pattern import NotePattern
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Create a new note pattern
@router.post("/note-patterns", response_model=NotePattern)
async def create_note_pattern(note_pattern: NotePattern, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    try:
        logger.info(f"Creating note pattern: {note_pattern}")
        result = await db.note_patterns.insert_one(note_pattern.dict())
        note_pattern.id = str(result.inserted_id)
        logger.info(f"Note pattern created with ID: {note_pattern.id}")
        return note_pattern
    except Exception as e:
        logger.error(f"Error creating note pattern: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get a single note pattern by ID
@router.get("/note-patterns/{pattern_id}")
async def get_note_pattern(pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Fetching note pattern with ID: {pattern_id}")
    note_pattern = await db.note_patterns.find_one({"_id": ObjectId(pattern_id)})
    if note_pattern is None:
        logger.warning(f"Note pattern not found for ID: {pattern_id}")
        raise HTTPException(status_code=404, detail="Note pattern not found")
    return note_pattern

# Get all note patterns
@router.get("/note-patterns", response_model=List[NotePattern])
async def get_note_patterns(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Fetching all note patterns")
    note_patterns = await db.note_patterns.find().to_list(length=None)
    return note_patterns
