# src/note_gen/routers/note_pattern_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from motor import motor_asyncio
from src.note_gen.dependencies import get_db
from src.note_gen.models.note_pattern import NotePattern, NotePatternResponse
from src.note_gen.models.note import Note
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Create a new note pattern
@router.post("/note_patterns/", response_model=NotePatternResponse)
async def create_note_pattern(note_pattern: NotePattern, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> NotePatternResponse:
    """Create a new note pattern."""
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
        return NotePatternResponse(**note_pattern.dict())
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error during note pattern creation: {e}")
        raise HTTPException(status_code=500, detail="Database error during creation")
    except Exception as e:
        logger.error(f"Unexpected error during note pattern creation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get a single note pattern by ID
@router.get("/note_patterns/{note_pattern_id}/", response_model=NotePatternResponse)
async def read_note_pattern(note_pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> NotePatternResponse:
    """Retrieve a note pattern by ID."""
    logger.info(f"Fetching note pattern with ID: {note_pattern_id}")
    try:
        note_pattern = await db.note_patterns.find_one({"_id": ObjectId(note_pattern_id)})
        if note_pattern is None:
            logger.warning(f"Note pattern not found for ID: {note_pattern_id}")
            raise HTTPException(status_code=404, detail="Note pattern not found")
        return NotePatternResponse(**note_pattern)
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching note pattern with ID {note_pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching note pattern with ID {note_pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get all note patterns
@router.get("/note_patterns", response_model=List[NotePatternResponse])
async def get_note_patterns(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> List[NotePatternResponse]:
    logger.info("Fetching all note patterns")
    try:
        note_patterns = await db.note_patterns.find().to_list(length=None)
        logger.debug(f"Fetched {len(note_patterns)} note patterns from the database")
        return [NotePatternResponse(**note_pattern) for note_pattern in note_patterns]
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching note patterns: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching note patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Update a note pattern by ID
@router.put("/note_patterns/{note_pattern_id}/", response_model=NotePatternResponse)
async def update_note_pattern(note_pattern_id: str, note_pattern: NotePattern, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> NotePatternResponse:
    """Update a note pattern by ID."""
    logger.info(f"Updating note pattern with ID: {note_pattern_id}")
    try:
        result = await db.note_patterns.update_one({"_id": ObjectId(note_pattern_id)}, {"$set": note_pattern.dict()})
        if result.matched_count == 0:
            logger.warning(f"Note pattern not found for ID: {note_pattern_id}")
            raise HTTPException(status_code=404, detail="Note pattern not found")
        logger.info(f"Note pattern updated with ID: {note_pattern_id}")
        return NotePatternResponse(**note_pattern.dict())
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error updating note pattern with ID {note_pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during update")
    except Exception as e:
        logger.error(f"Error updating note pattern with ID {note_pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete a note pattern by ID
@router.delete("/note_patterns/{note_pattern_id}/")
async def delete_note_pattern(note_pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)) -> None:
    """Delete a note pattern by ID."""
    logger.info(f"Deleting note pattern with ID: {note_pattern_id}")
    try:
        result = await db.note_patterns.delete_one({"_id": ObjectId(note_pattern_id)})
        if result.deleted_count == 0:
            logger.warning(f"Note pattern not found for ID: {note_pattern_id}")
            raise HTTPException(status_code=404, detail="Note pattern not found")
        logger.info(f"Note pattern deleted with ID: {note_pattern_id}")
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error deleting note pattern with ID {note_pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during deletion")
    except Exception as e:
        logger.error(f"Error deleting note pattern with ID {note_pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
