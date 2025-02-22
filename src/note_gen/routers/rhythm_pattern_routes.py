"""
Consolidated routes for rhythm pattern operations with improved error handling and logging.
"""
import sys
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from typing import List, Dict, Optional
from bson import ObjectId
from bson.errors import InvalidId
import logging
import uuid
import traceback
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.rhythm_pattern import RhythmPattern, RhythmPatternResponse, RhythmPatternCreate
from fastapi.encoders import jsonable_encoder

# Configure logging
logger = logging.getLogger(__name__)

# Create router with tags
logger.debug("Creating rhythm pattern router...")
router = APIRouter(
    tags=["rhythm-patterns"]
)
logger.debug("Router created")

@router.get("/")
async def get_rhythm_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[RhythmPatternResponse]:
    """Get all rhythm patterns."""
    try:
        cursor = db.rhythm_patterns.find({})
        patterns = await cursor.to_list(length=None)
        return [RhythmPatternResponse(**pattern) for pattern in patterns]
    except Exception as e:
        logger.error(f"Error retrieving rhythm patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{pattern_id}")
async def get_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """Get a specific rhythm pattern by ID."""
    try:
        pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if pattern:
            return RhythmPatternResponse(**pattern)
        raise HTTPException(status_code=404, detail=f"Rhythm pattern {pattern_id} not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid pattern ID format")
    except Exception as e:
        logger.error(f"Error retrieving rhythm pattern {pattern_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api/v1/rhythm-patterns", response_model=RhythmPatternResponse)
async def create_rhythm_pattern(
    pattern: RhythmPatternCreate,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """Create a new rhythm pattern."""
    try:
        logger.debug(f"Creating rhythm pattern: {pattern.name}")
        created_pattern = await db.rhythm_patterns.insert_one(pattern.dict())
        logger.info(f"Rhythm pattern created with ID: {created_pattern.inserted_id}")
        return RhythmPatternResponse(**pattern.dict())
    except DuplicateKeyError:
        logger.error(f"Duplicate key error when creating rhythm pattern: {pattern.name}")
        raise HTTPException(status_code=409, detail="Rhythm pattern with this ID already exists")
    except ValidationError as e:
        logger.error(f"Validation error when creating rhythm pattern: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-rhythm-pattern", response_model=RhythmPatternResponse)
async def generate_rhythm_pattern(
    rhythm_pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """
    Generate a rhythm pattern based on provided parameters.
    """
    # Logic to generate rhythm pattern
    return rhythm_pattern

@router.put("/{pattern_id}", response_model=RhythmPatternResponse)
async def update_rhythm_pattern(
    pattern_id: str,
    rhythm_pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPatternResponse:
    """Update an existing rhythm pattern."""
    try:
        existing = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        
        update_data = jsonable_encoder(rhythm_pattern)
        update_data["_id"] = pattern_id
        
        result = await db.rhythm_patterns.replace_one(
            {"_id": pattern_id},
            update_data
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=304, detail="No changes made to rhythm pattern")
        
        updated = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if updated:
            return RhythmPatternResponse(**updated)
        raise HTTPException(status_code=404, detail="Updated pattern not found")
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating rhythm pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> Response:
    """Delete a rhythm pattern."""
    try:
        result = await db.rhythm_patterns.delete_one({"_id": pattern_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Rhythm pattern not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")