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
from src.note_gen.models.chord_progression import ChordProgression, ChordProgressionResponse
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.chord import Chord

# Configure logging
logger = logging.getLogger(__name__)

# Create a router with specific tags
router = APIRouter(
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
    if not chord_progression.chords:
        raise ValueError("Chord progression must contain at least one chord")
    
    for chord in chord_progression.chords:
        if not isinstance(chord, Chord):
            raise ValueError("Each element in chords must be a valid Chord object")
        if not chord.root:
            raise ValueError("Each chord must have a root note")
        if not chord.quality:
            raise ValueError("Each chord must have a quality")
        if not isinstance(chord.quality, ChordQualityType):
            raise ValueError("Chord quality must be a valid ChordQualityType")

@router.post("/", response_model=ChordProgressionResponse, status_code=status.HTTP_201_CREATED)
async def create_chord_progression(
    chord_progression: ChordProgression,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> ChordProgressionResponse:
    """Create a new chord progression."""
    try:
        # Validate the chord progression
        _validate_chord_progression(chord_progression)
        
        # Prepare data for insertion
        progression_data = jsonable_encoder(chord_progression)
        
        # Insert into database
        result = await db.chord_progressions.insert_one(progression_data)
        
        # Retrieve the created progression
        created_progression = await db.chord_progressions.find_one(
            {"_id": result.inserted_id}
        )
        
        if not created_progression:
            raise HTTPException(
                status_code=404,
                detail="Created progression not found"
            )
            
        return ChordProgressionResponse(**created_progression)
        
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="Chord progression with this ID already exists"
        )
    except Exception as e:
        logger.error(f"Error creating chord progression: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/generate-chord-progression", response_model=ChordProgressionResponse)
async def generate_chord_progression(
    chord_progression: ChordProgression,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """
    Generate a chord progression based on provided parameters.
    """
    # Logic to generate chord progression
    return chord_progression

@router.get("/", response_model=List[ChordProgressionResponse])
async def get_chord_progressions(
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> List[ChordProgressionResponse]:
    """Get all chord progressions."""
    try:
        cursor = db.chord_progressions.find({})
        progressions = await cursor.to_list(length=None)
        return [ChordProgressionResponse(**prog) for prog in progressions]
    except Exception as e:
        logger.error(f"Error retrieving chord progressions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{progression_id}", response_model=ChordProgressionResponse)
async def get_chord_progression(
    progression_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> ChordProgressionResponse:
    """Get a specific chord progression by ID."""
    try:
        progression = await db.chord_progressions.find_one({"_id": progression_id})
        if not progression:
            raise HTTPException(
                status_code=404,
                detail="Chord progression not found"
            )
        return ChordProgressionResponse(**progression)
    except Exception as e:
        logger.error(f"Error retrieving chord progression: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{progression_id}", response_model=ChordProgressionResponse)
async def update_chord_progression(
    progression_id: str,
    chord_progression: ChordProgression,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> ChordProgressionResponse:
    """Update an existing chord progression."""
    try:
        # Validate the chord progression
        _validate_chord_progression(chord_progression)
        
        # Check if progression exists
        existing = await db.chord_progressions.find_one({"_id": progression_id})
        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Chord progression not found"
            )
        
        # Prepare update data
        update_data = jsonable_encoder(chord_progression)
        update_data["_id"] = progression_id
        
        # Update in database
        result = await db.chord_progressions.replace_one(
            {"_id": progression_id},
            update_data
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=304,
                detail="No changes made to chord progression"
            )
        
        # Retrieve updated progression
        updated = await db.chord_progressions.find_one({"_id": progression_id})
        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Updated progression not found"
            )
            
        return ChordProgressionResponse(**updated)
        
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="Chord progression with this ID already exists"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chord progression: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{progression_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chord_progression(
    progression_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """Delete a chord progression."""
    try:
        result = await db.chord_progressions.delete_one({"_id": progression_id})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Chord progression not found"
            )
    except Exception as e:
        logger.error(f"Error deleting chord progression: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")