"""
Consolidated routes for note pattern operations with improved error handling and logging.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from src.note_gen.dependencies import get_db
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
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> NotePatternResponse:
    """
    Create a new note pattern with comprehensive validation and error handling.
    
    Args:
        note_pattern (NotePattern): The note pattern to create
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        NotePatternResponse: Created note pattern with assigned ID
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        logger.info(f"Attempting to create note pattern: {note_pattern}")
        
        # Validate pattern name
        if not note_pattern.name or len(note_pattern.name.strip()) < 3:
            raise ValueError("Note pattern name must be at least 3 characters long")
        
        # Validate pattern intervals
        if not isinstance(note_pattern.pattern, list):
            raise ValueError("Pattern must be a list of integers")
        
        if not all(isinstance(interval, int) for interval in note_pattern.pattern):
            raise ValueError("All pattern intervals must be integers")
        
        # Optional: Add range validation for intervals
        if any(abs(interval) > 12 for interval in note_pattern.pattern):
            raise ValueError("Interval values should be within -12 to 12 semitones")
        
        # Check for duplicate pattern
        existing_pattern = await db.note_patterns.find_one({"name": note_pattern.name})
        if existing_pattern:
            logger.warning(f"Note pattern with name '{note_pattern.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Note pattern with name '{note_pattern.name}' already exists"
            )
        
        # Prepare pattern for database insertion
        pattern_dict = note_pattern.model_dump(by_alias=True)
        
        # Insert into database
        result = await db.note_patterns.insert_one(pattern_dict)
        pattern_dict["id"] = str(result.inserted_id)
        
        # Create and return response
        created_pattern = NotePatternResponse(**pattern_dict)
        logger.info(f"Successfully created note pattern with ID: {created_pattern.id}")
        return created_pattern
    
    except ValueError as ve:
        logger.error(f"Validation error during note pattern creation: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(ve)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during note pattern creation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during note pattern creation"
        )

@router.get("/", response_model=List[NotePatternResponse])
async def get_note_patterns(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[NotePatternResponse]:
    """
    Retrieve all note patterns from the database.
    
    Args:
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        List[NotePatternResponse]: List of all note patterns
    """
    try:
        logger.info("Fetching all note patterns")
        
        # Fetch all note patterns
        cursor = db.note_patterns.find()
        note_patterns = await cursor.to_list(length=None)
        
        # Convert to response models
        pattern_responses = [
            NotePatternResponse(**{**pattern, "id": str(pattern["_id"])}) 
            for pattern in note_patterns
        ]
        
        logger.info(f"Retrieved {len(pattern_responses)} note patterns")
        return pattern_responses
    
    except Exception as e:
        logger.error(f"Error retrieving note patterns: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unable to retrieve note patterns"
        )

@router.get("/{pattern_id}", response_model=NotePatternResponse)
async def get_note_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> NotePatternResponse:
    """
    Retrieve a specific note pattern by its ID.
    
    Args:
        pattern_id (str): The unique identifier of the note pattern
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        NotePatternResponse: The requested note pattern
    
    Raises:
        HTTPException: If the note pattern is not found
    """
    try:
        logger.info(f"Fetching note pattern with ID: {pattern_id}")
        
        # Find the pattern
        pattern = await db.note_patterns.find_one({"_id": pattern_id})
        
        if not pattern:
            logger.warning(f"Note pattern not found with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Note pattern with ID {pattern_id} not found"
            )
        
        # Convert to response model
        pattern_response = NotePatternResponse(**{**pattern, "id": str(pattern["_id"])})
        
        logger.info(f"Successfully retrieved note pattern: {pattern_id}")
        return pattern_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving note pattern {pattern_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error while fetching note pattern"
        )

@router.put("/{pattern_id}", response_model=NotePatternResponse)
async def update_note_pattern(
    pattern_id: str, 
    note_pattern: NotePattern, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> NotePatternResponse:
    """
    Update an existing note pattern.
    
    Args:
        pattern_id (str): The unique identifier of the note pattern to update
        note_pattern (NotePattern): Updated note pattern data
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        NotePatternResponse: The updated note pattern
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        logger.info(f"Attempting to update note pattern: {pattern_id}")
        
        # Validate pattern name
        if not note_pattern.name or len(note_pattern.name.strip()) < 3:
            raise ValueError("Note pattern name must be at least 3 characters long")
        
        # Validate pattern intervals
        if not isinstance(note_pattern.pattern, list):
            raise ValueError("Pattern must be a list of integers")
        
        if not all(isinstance(interval, int) for interval in note_pattern.pattern):
            raise ValueError("All pattern intervals must be integers")
        
        # Optional: Add range validation for intervals
        if any(abs(interval) > 12 for interval in note_pattern.pattern):
            raise ValueError("Interval values should be within -12 to 12 semitones")
        
        # Prepare update data
        update_data = note_pattern.model_dump(by_alias=True, exclude_unset=True)
        
        # Update the pattern
        result = await db.note_patterns.update_one(
            {"_id": pattern_id}, 
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No note pattern found to update with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Note pattern with ID {pattern_id} not found"
            )
        
        # Fetch updated pattern
        updated_pattern = await db.note_patterns.find_one({"_id": pattern_id})
        updated_pattern_response = NotePatternResponse(**{**updated_pattern, "id": str(updated_pattern["_id"])})
        
        logger.info(f"Successfully updated note pattern: {pattern_id}")
        return updated_pattern_response
    
    except ValueError as ve:
        logger.error(f"Validation error during note pattern update: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(ve)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note pattern {pattern_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during note pattern update"
        )

@router.delete("/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_pattern(
    pattern_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Delete a note pattern by its ID.
    
    Args:
        pattern_id (str): The unique identifier of the note pattern to delete
        db (AsyncIOMotorDatabase): Database connection
    
    Raises:
        HTTPException: If the note pattern cannot be deleted
    """
    try:
        logger.info(f"Attempting to delete note pattern: {pattern_id}")
        
        # Delete the pattern
        result = await db.note_patterns.delete_one({"_id": pattern_id})
        
        if result.deleted_count == 0:
            logger.warning(f"No note pattern found to delete with ID: {pattern_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Note pattern with ID {pattern_id} not found"
            )
        
        logger.info(f"Successfully deleted note pattern: {pattern_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note pattern {pattern_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during note pattern deletion"
        )
