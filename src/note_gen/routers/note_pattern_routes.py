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
    logger.info(f"Incoming request to create note pattern: {note_pattern}")
    # Validate required fields
    required_fields = ['name', 'pattern']
    missing_fields = [field for field in required_fields if not getattr(note_pattern, field)]
    if missing_fields:
        logger.error(f"Missing required fields: {', '.join(missing_fields)}")
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")
    try:
        logger.info(f"Creating note pattern: {note_pattern}")
        result = await db.note_patterns.insert_one(note_pattern.dict())
        note_pattern.id = str(result.inserted_id)
        logger.info(f"Note pattern created with ID: {note_pattern.id}")
        return note_pattern
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error during note pattern creation: {e}")
        raise HTTPException(status_code=500, detail="Database error during creation")
    except Exception as e:
        logger.error(f"Unexpected error during note pattern creation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get a single note pattern by ID
@router.get("/note-patterns/{pattern_id}")
async def get_note_pattern(pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info(f"Fetching note pattern with ID: {pattern_id}")
    try:
        note_pattern = await db.note_patterns.find_one({"_id": ObjectId(pattern_id)})
        if note_pattern is None:
            logger.warning(f"Note pattern not found for ID: {pattern_id}")
            raise HTTPException(status_code=404, detail="Note pattern not found")
        return note_pattern
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching note pattern with ID {pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching note pattern with ID {pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get all note patterns
@router.get("/note-patterns", response_model=List[NotePattern])
async def get_note_patterns(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Fetching all note patterns")
    try:
        note_patterns = await db.note_patterns.find().to_list(length=None)
        logger.debug(f"Fetched {len(note_patterns)} note patterns from the database")
        return note_patterns
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching note patterns: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching note patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
