"""
Consolidated routes for chord progression operations with improved error handling and logging.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from src.note_gen.dependencies import get_db
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionResponse
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.chord import Chord

# Configure logging
logger = logging.getLogger(__name__)

# Create a router with a specific prefix and tags
router = APIRouter(
    prefix="/chord-progressions",
    tags=["chord-progressions"]
)

def _validate_chord_progression(chord_progression: ChordProgression):
    """
    Validate chord progression with comprehensive checks.
    
    Args:
        chord_progression (ChordProgression): Chord progression to validate
    
    Raises:
        ValueError: If validation fails
    """
    # Validate required fields
    required_fields = ['name', 'chords', 'key', 'scale_type']
    missing_fields = [field for field in required_fields if not getattr(chord_progression, field)]
    if missing_fields:
        raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')
    
    # Validate chords
    if not chord_progression.chords:
        raise ValueError("Chord progression must have at least one chord")
    
    # Validate key and scale type
    if not chord_progression.key or not chord_progression.scale_type:
        raise ValueError("Key and scale type must be specified")

@router.post("/", response_model=ChordProgressionResponse, status_code=status.HTTP_201_CREATED)
async def create_chord_progression(
    chord_progression: ChordProgression, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> ChordProgressionResponse:
    """
    Create a new chord progression with comprehensive validation and error handling.
    
    Args:
        chord_progression (ChordProgression): The chord progression to create
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        ChordProgressionResponse: Created chord progression with assigned ID
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        logger.info(f"Attempting to create chord progression: {chord_progression}")
        
        # Validate chord progression
        _validate_chord_progression(chord_progression)
        
        # Check for duplicate progression
        existing_progression = await db.chord_progressions.find_one({"name": chord_progression.name})
        if existing_progression:
            logger.warning(f"Chord progression with name '{chord_progression.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"Chord progression with name '{chord_progression.name}' already exists"
            )
        
        # Prepare progression for database insertion
        pattern_dict = chord_progression.model_dump(by_alias=True)
        
        # Insert into database
        result = await db.chord_progressions.insert_one(pattern_dict)
        pattern_dict["id"] = str(result.inserted_id)
        
        # Create and return response
        created_progression = ChordProgressionResponse(**pattern_dict)
        logger.info(f"Successfully created chord progression with ID: {created_progression.id}")
        return created_progression
    
    except ValueError as ve:
        logger.error(f"Validation error during chord progression creation: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(ve)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during chord progression creation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during chord progression creation"
        )

@router.get("/", response_model=List[ChordProgressionResponse])
async def get_chord_progressions(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[ChordProgressionResponse]:
    """
    Retrieve all chord progressions from the database.
    
    Args:
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        List[ChordProgressionResponse]: List of all chord progressions
    """
    try:
        logger.info("Fetching all chord progressions")
        
        # Fetch all chord progressions
        cursor = db.chord_progressions.find()
        chord_progressions = await cursor.to_list(length=None)
        
        # Convert to response models
        progression_responses = [
            ChordProgressionResponse(**{**progression, "id": str(progression["_id"])}) 
            for progression in chord_progressions
        ]
        
        logger.info(f"Retrieved {len(progression_responses)} chord progressions")
        return progression_responses
    
    except Exception as e:
        logger.error(f"Error retrieving chord progressions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unable to retrieve chord progressions"
        )

@router.get("/{progression_id}", response_model=ChordProgressionResponse)
async def get_chord_progression(
    progression_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> ChordProgressionResponse:
    """
    Retrieve a specific chord progression by its ID.
    
    Args:
        progression_id (str): The unique identifier of the chord progression
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        ChordProgressionResponse: The requested chord progression
    
    Raises:
        HTTPException: If the chord progression is not found
    """
    try:
        logger.info(f"Fetching chord progression with ID: {progression_id}")
        
        # Find the progression
        progression = await db.chord_progressions.find_one({"_id": progression_id})
        
        if not progression:
            logger.warning(f"Chord progression not found with ID: {progression_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Chord progression with ID {progression_id} not found"
            )
        
        # Convert to response model
        progression_response = ChordProgressionResponse(**{**progression, "id": str(progression["_id"])})
        
        logger.info(f"Successfully retrieved chord progression: {progression_id}")
        return progression_response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chord progression {progression_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error while fetching chord progression"
        )

@router.put("/{progression_id}", response_model=ChordProgressionResponse)
async def update_chord_progression(
    progression_id: str, 
    chord_progression: ChordProgression, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> ChordProgressionResponse:
    """
    Update an existing chord progression.
    
    Args:
        progression_id (str): The unique identifier of the chord progression to update
        chord_progression (ChordProgression): Updated chord progression data
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        ChordProgressionResponse: The updated chord progression
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        logger.info(f"Attempting to update chord progression: {progression_id}")
        
        # Validate chord progression
        _validate_chord_progression(chord_progression)
        
        # Prepare update data
        update_data = chord_progression.model_dump(by_alias=True, exclude_unset=True)
        
        # Update the progression
        result = await db.chord_progressions.update_one(
            {"_id": progression_id}, 
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            logger.warning(f"No chord progression found to update with ID: {progression_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Chord progression with ID {progression_id} not found"
            )
        
        # Fetch updated progression
        updated_progression = await db.chord_progressions.find_one({"_id": progression_id})
        updated_progression_response = ChordProgressionResponse(**{**updated_progression, "id": str(updated_progression["_id"])})
        
        logger.info(f"Successfully updated chord progression: {progression_id}")
        return updated_progression_response
    
    except ValueError as ve:
        logger.error(f"Validation error during chord progression update: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(ve)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chord progression {progression_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during chord progression update"
        )

@router.delete("/{progression_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chord_progression(
    progression_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Delete a chord progression by its ID.
    
    Args:
        progression_id (str): The unique identifier of the chord progression to delete
        db (AsyncIOMotorDatabase): Database connection
    
    Raises:
        HTTPException: If the chord progression cannot be deleted
    """
    try:
        logger.info(f"Attempting to delete chord progression: {progression_id}")
        
        # Delete the progression
        result = await db.chord_progressions.delete_one({"_id": progression_id})
        
        if result.deleted_count == 0:
            logger.warning(f"No chord progression found to delete with ID: {progression_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Chord progression with ID {progression_id} not found"
            )
        
        logger.info(f"Successfully deleted chord progression: {progression_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chord progression {progression_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during chord progression deletion"
        )