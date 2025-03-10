"""
Consolidated routes for rhythm pattern operations with improved error handling and logging.
"""
import sys
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from typing import List, Dict, Any, Optional
from bson import ObjectId
from bson.errors import InvalidId
import logging
import uuid
import traceback
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.patterns import RhythmPattern
from fastapi.encoders import jsonable_encoder

# Configure logging
logger = logging.getLogger(__name__)

# Create router with no prefix (prefix is added in __init__.py)
logger.debug("Creating rhythm pattern router...")
router = APIRouter()
logger.debug("Router created")

@router.get("/")
async def get_rhythm_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[RhythmPattern]:
    """Get all rhythm patterns."""
    try:
        cursor = db.rhythm_patterns.find({})
        patterns = await cursor.to_list(length=None)
        return [RhythmPattern(**pattern) for pattern in patterns]
    except Exception as e:
        logger.error(f"Error retrieving rhythm patterns: {str(e)}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content='{"detail": "Internal server error"}',
            media_type="application/json"
        )

@router.get("/{pattern_id}", response_model=RhythmPattern)
async def get_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPattern:
    """Get a rhythm pattern by ID."""
    try:
        # Convert string ID to ObjectId if it's a valid ObjectId format
        object_id = None
        if ObjectId.is_valid(pattern_id):
            try:
                object_id = ObjectId(pattern_id)
            except InvalidId:
                pass

        # Query the database with multiple possible ID formats
        pattern = None
        if object_id:
            # Try by ObjectId first
            pattern = await db.rhythm_patterns.find_one({"_id": object_id})
        
        # If not found by ObjectId, try by string id field
        if not pattern:
            pattern = await db.rhythm_patterns.find_one({"id": pattern_id})
        
        # Final fallback - try treating the string directly as _id
        if not pattern and not object_id:
            pattern = await db.rhythm_patterns.find_one({"_id": pattern_id})
        
        if not pattern:
            logger.warning(f"Rhythm pattern not found with id {pattern_id}")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=f'{{"detail": "Rhythm pattern {pattern_id} not found"}}',
                media_type="application/json"
            )
        
        # Ensure pattern has a string id field
        if "_id" in pattern and isinstance(pattern["_id"], ObjectId):
            pattern["id"] = str(pattern["_id"])
        
        logger.debug(f"Retrieved rhythm pattern: {pattern.get('name')}")
        return RhythmPattern(**pattern)
    except Exception as e:
        logger.error(f"Error retrieving rhythm pattern {pattern_id}: {e}", exc_info=True)
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f'{{"detail": "Error retrieving rhythm pattern: {str(e)}"}}',
            media_type="application/json"
        )

@router.post("/", response_model=RhythmPattern, status_code=status.HTTP_201_CREATED)
async def create_rhythm_pattern(
    pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPattern:
    """Create a new rhythm pattern."""
    if not pattern:
        logger.error("Received empty pattern data.")
        return Response(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='{"detail": "Pattern data cannot be empty"}',
            media_type="application/json"
        )
    
    logger.debug(f"Received request to create rhythm pattern: {pattern}")
    
    # Check if a pattern with the same name already exists
    existing_pattern = await db.rhythm_patterns.find_one({"name": pattern.name})
    if existing_pattern:
        logger.warning(f"Rhythm pattern with name '{pattern.name}' already exists")
        return Response(
            status_code=status.HTTP_409_CONFLICT,
            content=f'{{"detail": "Rhythm pattern with name \'{pattern.name}\' already exists"}}',
            media_type="application/json"
        )
        
    try:
        logger.debug(f"Creating rhythm pattern: {pattern.name}")
        pattern_dict = jsonable_encoder(pattern)
        
        # Ensure there's an id field
        if "id" not in pattern_dict or not pattern_dict["id"]:
            pattern_dict["id"] = str(uuid.uuid4())
            
        created_pattern = await db.rhythm_patterns.insert_one(pattern_dict)
        logger.info(f"Rhythm pattern created with ID: {created_pattern.inserted_id}")
        
        # Retrieve the created pattern to return it
        new_pattern = await db.rhythm_patterns.find_one({"_id": created_pattern.inserted_id})
        if not new_pattern:
            logger.error("Created pattern not found after insertion")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content='{"detail": "Created pattern not found"}',
                media_type="application/json"
            )
            
        # Ensure the response has an id field that's a string
        if "_id" in new_pattern and isinstance(new_pattern["_id"], ObjectId):
            if "id" not in new_pattern or not new_pattern["id"]:
                new_pattern["id"] = str(new_pattern["_id"])
                
        response_data = RhythmPattern(**new_pattern)
        logger.debug(f"Returning created pattern with id: {response_data.id}")
        return response_data
    except DuplicateKeyError:
        logger.error(f"Duplicate key error when creating rhythm pattern: {pattern.name}")
        return Response(
            status_code=status.HTTP_409_CONFLICT,
            content='{"detail": "Rhythm pattern with this ID already exists"}',
            media_type="application/json"
        )
    except ValidationError as e:
        logger.error(f"Validation error when creating rhythm pattern: {str(e)}")
        return Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=f'{{"detail": "{str(e)}"}}',
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error creating rhythm pattern: {e}", exc_info=True)
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f'{{"detail": "Internal server error: {str(e)}"}}',
            media_type="application/json"
        )

@router.post("/generate-rhythm-pattern", response_model=RhythmPattern)
async def generate_rhythm_pattern(
    rhythm_pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPattern:
    """
    Generate a rhythm pattern based on provided parameters.
    """
    logger.debug(f"Received request data for generating rhythm pattern: {rhythm_pattern}")
    # Logic to generate rhythm pattern
    return rhythm_pattern

@router.put("/{pattern_id}", response_model=RhythmPattern)
async def update_rhythm_pattern(
    pattern_id: str,
    rhythm_pattern: RhythmPattern,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> RhythmPattern:
    """Update an existing rhythm pattern."""
    logger.debug(f"Received request data for updating rhythm pattern: {rhythm_pattern}")
    try:
        existing = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if not existing:
            logger.error(f"Rhythm pattern not found: {pattern_id}")
            return Response(
                status_code=status.HTTP_404_NOT_FOUND,
                content=f'{{"detail": "Rhythm pattern {pattern_id} not found"}}',
                media_type="application/json"
            )
        
        update_data = jsonable_encoder(rhythm_pattern)
        update_data["_id"] = pattern_id
        
        result = await db.rhythm_patterns.replace_one(
            {"_id": pattern_id},
            update_data
        )
        
        if result.modified_count == 0:
            logger.warning("No changes made to rhythm pattern")
            return Response(
                status_code=status.HTTP_304_NOT_MODIFIED,
                content='{"detail": "No changes made to rhythm pattern"}',
                media_type="application/json"
            )
        
        updated = await db.rhythm_patterns.find_one({"_id": pattern_id})
        if updated:
            return RhythmPattern(**updated)
        logger.error("Updated pattern not found")
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content='{"detail": "Updated pattern not found"}',
            media_type="application/json"
        )
    except ValidationError as e:
        logger.error(f"Validation error when updating rhythm pattern: {str(e)}")
        return Response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=f'{{"detail": "{str(e)}"}}',
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error updating rhythm pattern: {str(e)}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f'{{"detail": "Internal server error: {str(e)}"}}',
            media_type="application/json"
        )

@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rhythm_pattern(
    pattern_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> Response:
    """Delete a rhythm pattern."""
    logger.debug(f"Received request data for deleting rhythm pattern ID: {pattern_id}")
    try:
        # Convert string ID to ObjectId if it's a valid ObjectId format
        if ObjectId.is_valid(pattern_id):
            try:
                object_id = ObjectId(pattern_id)
                # Try to find the pattern first
                pattern = await db.rhythm_patterns.find_one({"_id": object_id})
                if pattern:
                    result = await db.rhythm_patterns.delete_one({"_id": object_id})
                    if result.deleted_count > 0:
                        logger.info(f"Successfully deleted rhythm pattern with ObjectId: {pattern_id}")
                        return Response(status_code=status.HTTP_204_NO_CONTENT)
            except InvalidId:
                logger.warning(f"Invalid ObjectId format: {pattern_id}")
        
        # Try by string id field
        pattern = await db.rhythm_patterns.find_one({"id": pattern_id})
        if pattern:
            result = await db.rhythm_patterns.delete_one({"id": pattern_id})
            if result.deleted_count > 0:
                logger.info(f"Successfully deleted rhythm pattern with string id: {pattern_id}")
                return Response(status_code=status.HTTP_204_NO_CONTENT)
        
        # Final attempt with pattern_id as string _id
        if not ObjectId.is_valid(pattern_id):
            result = await db.rhythm_patterns.delete_one({"_id": pattern_id})
            if result.deleted_count > 0:
                logger.info(f"Successfully deleted rhythm pattern with string _id: {pattern_id}")
                return Response(status_code=status.HTTP_204_NO_CONTENT)
                
        logger.error(f"Rhythm pattern not found: {pattern_id}")
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=f'{{"detail": "Rhythm pattern {pattern_id} not found"}}',
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error deleting rhythm pattern: {str(e)}")
        return Response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f'{{"detail": "Error deleting rhythm pattern: {str(e)}"}}',
            media_type="application/json"
        )