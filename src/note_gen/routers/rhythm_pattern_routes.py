# src/note_gen/routers/rhythm_pattern_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from motor import motor_asyncio
from src.note_gen.dependencies import get_db
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

async def create_rhythm_pattern_in_db(pattern: RhythmPattern, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Incoming request to create rhythm pattern: {pattern}")
    # Validate required fields
    required_fields = ['name', 'pattern']
    missing_fields = [field for field in required_fields if not getattr(pattern, field)]
    if missing_fields:
        logger.error(f"Missing required fields: {', '.join(missing_fields)}")
        raise HTTPException(status_code=400, detail=f'Missing required fields: {", ".join(missing_fields)}')
    try:
        logger.info(f"Creating rhythm pattern: {pattern}")
        result = await db.rhythm_patterns.insert_one(pattern.dict())
        pattern.id = str(result.inserted_id)
        logger.info(f"Rhythm pattern created with ID: {pattern.id}")
        return RhythmPatternResponse(**pattern.dict())
    except motor_asyncio.errors.DuplicateKeyError as e:
        logger.error(f"Rhythm pattern with the same name already exists: {e}")
        raise HTTPException(status_code=400, detail="Rhythm pattern with the same name already exists")
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error during rhythm pattern creation: {e}")
        raise HTTPException(status_code=500, detail="Database error during creation")
    except Exception as e:
        logger.error(f"Unexpected error during rhythm pattern creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/rhythm_patterns/", response_model=RhythmPatternResponse)
async def create_rhythm_pattern(rhythm_pattern: RhythmPattern, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new rhythm pattern."""
    db_rhythm_pattern = await create_rhythm_pattern_in_db(rhythm_pattern, db)
    return db_rhythm_pattern

async def get_rhythm_pattern_from_db(pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Fetching rhythm pattern with ID: {pattern_id}")
    try:
        if not ObjectId.is_valid(pattern_id):
            logger.error(f"Invalid pattern ID: {pattern_id}")
            raise HTTPException(status_code=400, detail="Invalid pattern ID")
        pattern = await db.rhythm_patterns.find_one({"_id": ObjectId(pattern_id)})
        if pattern is None:
            logger.warning(f"Rhythm pattern not found for ID: {pattern_id}")
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        logger.info(f"Fetched rhythm pattern: {pattern}")
        return RhythmPatternResponse(**pattern)
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching rhythm pattern with ID {pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern with ID {pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/rhythm_patterns/{rhythm_pattern_id}/", response_model=RhythmPatternResponse)
async def read_rhythm_pattern(rhythm_pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Retrieve a rhythm pattern by ID."""
    rhythm_pattern = await get_rhythm_pattern_from_db(rhythm_pattern_id, db)
    return rhythm_pattern

async def update_rhythm_pattern_in_db(pattern_id: str, pattern: RhythmPattern, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Updating rhythm pattern with ID: {pattern_id}")
    try:
        if not ObjectId.is_valid(pattern_id):
            logger.error(f"Invalid pattern ID: {pattern_id}")
            raise HTTPException(status_code=400, detail="Invalid pattern ID")
        updated_pattern = await db.rhythm_patterns.find_one_and_update({"_id": ObjectId(pattern_id)}, {"$set": pattern.dict(exclude_unset=True)})
        if updated_pattern is None:
            logger.warning(f"Rhythm pattern not found for ID: {pattern_id}")
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        logger.info(f"Updated rhythm pattern: {updated_pattern}")
        return RhythmPatternResponse(**updated_pattern)
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error updating rhythm pattern with ID {pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during update")
    except Exception as e:
        logger.error(f"Error updating rhythm pattern with ID {pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/rhythm_patterns/{rhythm_pattern_id}/", response_model=RhythmPatternResponse)
async def update_rhythm_pattern(rhythm_pattern_id: str, rhythm_pattern: RhythmPattern, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Update a rhythm pattern by ID."""
    updated_rhythm_pattern = await update_rhythm_pattern_in_db(rhythm_pattern_id, rhythm_pattern, db)
    return updated_rhythm_pattern

async def delete_rhythm_pattern_from_db(pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase):
    logger.info(f"Deleting rhythm pattern with ID: {pattern_id}")
    try:
        if not ObjectId.is_valid(pattern_id):
            logger.error(f"Invalid pattern ID: {pattern_id}")
            raise HTTPException(status_code=400, detail="Invalid pattern ID")
        result = await db.rhythm_patterns.delete_one({"_id": ObjectId(pattern_id)})
        if result.deleted_count == 0:
            logger.warning(f"Rhythm pattern not found for ID: {pattern_id}")
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        logger.info(f"Deleted rhythm pattern with ID: {pattern_id}")
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error deleting rhythm pattern with ID {pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during deletion")
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern with ID {pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/rhythm_patterns/{rhythm_pattern_id}/")
async def delete_rhythm_pattern(rhythm_pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    """Delete a rhythm pattern by ID."""
    await delete_rhythm_pattern_from_db(rhythm_pattern_id, db)

# Get all rhythm patterns
@router.get("/rhythm-patterns", response_model=List[RhythmPatternResponse])
async def get_rhythm_patterns(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Fetching all rhythm patterns")
    try:
        patterns = await db.rhythm_patterns.find().to_list(length=None)
        logger.debug(f"Fetched {len(patterns)} rhythm patterns from the database")
        return [RhythmPatternResponse(**pattern) for pattern in patterns]
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching rhythm patterns: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
