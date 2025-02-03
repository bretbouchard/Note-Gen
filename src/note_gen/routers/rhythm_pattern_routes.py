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
        return pattern
    except motor_asyncio.errors.DuplicateKeyError as e:
        logger.error(f"Rhythm pattern with the same name already exists: {e}")
        raise HTTPException(status_code=400, detail="Rhythm pattern with the same name already exists")
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error during rhythm pattern creation: {e}")
        raise HTTPException(status_code=500, detail="Database error during creation")
    except Exception as e:
        logger.error(f"Unexpected error during rhythm pattern creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get a single rhythm pattern by ID
@router.get("/rhythm-patterns/{pattern_id}")
async def get_rhythm_pattern(pattern_id: str, db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
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
        return pattern
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching rhythm pattern with ID {pattern_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching rhythm pattern with ID {pattern_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get all rhythm patterns
@router.get("/rhythm-patterns", response_model=List[RhythmPattern])
async def get_rhythm_patterns(db: motor_asyncio.AsyncIOMotorDatabase = Depends(get_db)):
    logger.info("Fetching all rhythm patterns")
    try:
        patterns = await db.rhythm_patterns.find().to_list(length=None)
        logger.debug(f"Fetched {len(patterns)} rhythm patterns from the database")
        return patterns
    except motor_asyncio.errors.PyMongoError as e:
        logger.error(f"Database error fetching rhythm patterns: {e}")
        raise HTTPException(status_code=500, detail="Database error during fetch")
    except Exception as e:
        logger.error(f"Error fetching rhythm patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
