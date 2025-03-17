"""
Consolidated routes for chord progression operations with improved error handling and logging.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from fastapi.encoders import jsonable_encoder
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.chord_progression_extras import ChordProgressionResponse
from src.note_gen.models.patterns import ChordProgression
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note import Note  # Import the Note model

import logging
# Configure logging
logger = logging.getLogger(__name__)

# Create a router with specific tags
router = APIRouter(
    tags=["chord-progressions"]
)

def _validate_chord_progression(chord_progression: ChordProgression) -> None:
    """
    Validate chord progression with comprehensive checks.
    
    Args:
        chord_progression (ChordProgression): Chord progression to validate
    
    Raises:
        ValueError: If validation fails
    """
    if not chord_progression.chords:
        raise ValueError("Chord progression must contain at least one chord")
    
    for chord in chord_progression.chords:
        logger.debug(f"Validating chord: root={chord.root}, quality={chord.quality}")
        logger.debug(f"Chord details: {chord}")  # Log the chord details
        if not isinstance(chord, Chord):
            logger.error(f"Invalid chord object: {chord}")
            raise ValueError("Each element in chords must be a valid Chord object")
            
        if not chord.root:
            logger.error(f"Chord missing root: {chord}")
            raise ValueError("Each chord must have a root")
        # Check if root is a Note instance or a dictionary with proper fields
        if isinstance(chord.root, Note):
            # Note instance is valid
            pass
        elif isinstance(chord.root, dict):
            if not chord.root.get("note_name") or not chord.root.get("octave"):
                logger.error(f"Chord root must contain 'note_name' and 'octave': {chord.root}")
                raise ValueError("Chord root must contain 'note_name' and 'octave'")
        else:
            logger.error(f"Chord root must be a Note instance or a dictionary: {chord.root}")
            raise ValueError("Chord root must be a Note instance or a dictionary")
        if not chord.quality:
            logger.error(f"Chord without quality: {chord}")
            raise ValueError("Each chord must have a quality")
        if isinstance(chord.quality, str):
            logger.debug(f"Validating chord quality: {chord.quality}")
            try:
                # Use ChordQuality.from_string instead of indexing
                chord.quality = ChordQuality.from_string(chord.quality)
                logger.info(f"Chord quality '{chord.quality}' is valid")
            except ValueError:
                logger.error(f"Invalid chord quality encountered: {chord.quality}")
                raise ValueError(f"Chord quality '{chord.quality}' is not a valid ChordQuality")
        # Check if quality is a valid ChordQuality enum instance
        if not isinstance(chord.quality, ChordQuality):
            raise ValueError("Chord quality must be a valid Chord.quality")

@router.post("", response_model=ChordProgressionResponse, status_code=status.HTTP_201_CREATED)
async def create_chord_progression(
    chord_progression: ChordProgression,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db_conn)
) -> ChordProgressionResponse:
    """Create a new chord progression."""
    logger.info(f"Incoming request to create chord progression with data: {chord_progression}")
    try:
        # Validate the chord progression
        _validate_chord_progression(chord_progression)
        
        # Prepare data for insertion
        progression_data = jsonable_encoder(chord_progression)
        logger.info(f"Inserting chord progression into database: {progression_data}")
        
        # Insert into database
        result = await db.chord_progressions.insert_one(progression_data)
        logger.info(f"Successfully created chord progression with ID: {result.inserted_id}")
        
        # Retrieve the created progression
        created_progression = await db.chord_progressions.find_one(
            {"_id": result.inserted_id}
        )

        if not created_progression:
            logger.error("Created progression not found in the database.")
            raise HTTPException(
                status_code=404,
                detail="Created progression not found"
            )
        
        # Cast the response to ChordProgressionResponse type
        response = ChordProgressionResponse(**created_progression)
        return response
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))
    except DuplicateKeyError:
        logger.error("Duplicate key error while inserting chord progression.")
        raise HTTPException(
            status_code=409,
            detail="Chord progression with this ID already exists"
        )
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("", response_model=List[ChordProgressionResponse])
async def get_chord_progressions(
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db_conn)
) -> List[ChordProgressionResponse]:
    """Get all chord progressions."""
    logger.info("Incoming request to retrieve chord progressions")
    try:
        # Retrieve all progressions from the database
        progressions = await db.chord_progressions.find().to_list(length=None)
        logger.info(f"Retrieved {len(progressions)} chord progressions from the database.")
        for prog in progressions:
            logger.debug(f"Progression details: {prog}")

        # Convert each progression to ChordProgressionResponse with proper typing
        result: List[ChordProgressionResponse] = []
        for prog in progressions:
            # Cast the response to ChordProgressionResponse type
            response = ChordProgressionResponse(**prog)
            result.append(response)
        return result
    except Exception as e:
        logger.error(f"Error retrieving chord progressions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{progression_id}", response_model=ChordProgressionResponse)
async def get_chord_progression(
    progression_id: str,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db_conn)
) -> ChordProgressionResponse:
    """Get a specific chord progression by its ID."""
    logger.info(f"Incoming request to retrieve chord progression with ID: {progression_id}")
    try:
        # Validate the ID
        if not ObjectId.is_valid(progression_id):
            logger.error(f"Invalid progression ID format: {progression_id}")
            raise HTTPException(status_code=400, detail="Invalid progression ID format")

        # Retrieve the progression from the database
        progression = await db.chord_progressions.find_one({"_id": ObjectId(progression_id)})

        if progression is None:
            logger.error(f"Chord progression not found with ID: {progression_id}")
            raise HTTPException(
                status_code=404,
                detail="Chord progression not found"
            )
        # Cast the response to ChordProgressionResponse type
        response = ChordProgressionResponse(**progression)
        return response
    except Exception as e:
        logger.error(f"Error retrieving chord progression: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{progression_id}", response_model=ChordProgressionResponse)
async def update_chord_progression(
    progression_id: str,
    chord_progression: ChordProgression,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db_conn)
) -> ChordProgressionResponse:
    """Update an existing chord progression by its ID."""
    logger.info(f"Incoming request to update chord progression with ID: {progression_id}, data: {chord_progression}")
    try:
        # Validate the ID
        if not ObjectId.is_valid(progression_id):
            logger.error(f"Invalid progression ID format: {progression_id}")
            raise HTTPException(status_code=400, detail="Invalid progression ID format")

        # Validate the chord progression
        _validate_chord_progression(chord_progression)

        # Prepare data for update
        progression_data = jsonable_encoder(chord_progression)

        # Update the progression in the database
        updated = await db.chord_progressions.find_one_and_update(
            {"_id": ObjectId(progression_id)},
            {"$set": progression_data},
            return_document=True
        )

        if updated is None:
            logger.error(f"Updated progression not found with ID: {progression_id}")
            raise HTTPException(
                status_code=404,
                detail="Updated progression not found"
            )
        # Cast the response to ChordProgressionResponse type
        response = ChordProgressionResponse(**updated)
        return response

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))
    except DuplicateKeyError:
        logger.error("Duplicate key error while updating chord progression.")
        raise HTTPException(
            status_code=409,
            detail="Chord progression with this ID already exists"
        )
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.delete("/{progression_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chord_progression(
    progression_id: str,
    db: AsyncIOMotorDatabase[Dict[str, Any]] = Depends(get_db_conn)
) -> None:
    """Delete a chord progression."""
    try:
        result = await db.chord_progressions.delete_one({"_id": ObjectId(progression_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Chord progression not found"
            )
    except Exception as e:
        logger.error(f"Error deleting chord progression: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )