"""
Consolidated routes for note pattern operations with improved error handling and logging.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Optional
from bson import ObjectId
from bson.errors import InvalidId
import logging
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.note_pattern import NotePattern, NotePatternResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create a router with a specific prefix and tags
router = APIRouter(
    tags=["note-patterns"]
)

@router.post("/", response_model=NotePatternResponse, status_code=status.HTTP_201_CREATED)
async def create_note_pattern(
    note_pattern: NotePattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NotePatternResponse:
    """Create a new note pattern."""
    try:
        pattern_data = jsonable_encoder(note_pattern)
        result = await db.note_patterns.insert_one(pattern_data)
        
        created_pattern = await db.note_patterns.find_one({"_id": result.inserted_id})
        if created_pattern:
            return NotePatternResponse(**created_pattern)
        raise HTTPException(status_code=404, detail="Created pattern not found")
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Note pattern with this ID already exists")
    except Exception as e:
        logger.error(f"Error creating note pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[NotePatternResponse])
async def get_note_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[NotePatternResponse]:
    """Get all note patterns."""
    try:
        cursor = db.note_patterns.find({})
        patterns = await cursor.to_list(length=None)
        return [NotePatternResponse(**pattern) for pattern in patterns]
    except Exception as e:
        logger.error(f"Error retrieving note patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{pattern_id}", response_model=NotePatternResponse)
async def get_note_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NotePatternResponse:
    """Get a specific note pattern by ID."""
    try:
        pattern = await db.note_patterns.find_one({"_id": pattern_id})
        if pattern:
            return NotePatternResponse(**pattern)
        raise HTTPException(status_code=404, detail="Note pattern not found")
    except Exception as e:
        logger.error(f"Error retrieving note pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{pattern_id}", response_model=NotePatternResponse)
async def update_note_pattern(
    pattern_id: str,
    note_pattern: NotePattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NotePatternResponse:
    """Update an existing note pattern."""
    try:
        existing = await db.note_patterns.find_one({"_id": pattern_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Note pattern not found")
        
        update_data = jsonable_encoder(note_pattern)
        update_data["_id"] = pattern_id
        
        result = await db.note_patterns.replace_one(
            {"_id": pattern_id},
            update_data
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=304, detail="No changes made to note pattern")
        
        updated = await db.note_patterns.find_one({"_id": pattern_id})
        if updated:
            return NotePatternResponse(**updated)
        raise HTTPException(status_code=404, detail="Updated pattern not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """Delete a note pattern."""
    try:
        result = await db.note_patterns.delete_one({"_id": pattern_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note pattern not found")
    except Exception as e:
        logger.error(f"Error deleting note pattern: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
