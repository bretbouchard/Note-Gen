"""
src/note_gen/routers/user_routes.py

User-related route handlers.
"""

from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from src.note_gen.models.request_models import GenerateSequenceRequest
from src.note_gen.generators.note_sequence_generator import generate_sequence_from_presets
from src.note_gen.database import (
    get_db,
    get_chord_progression_by_name,
    get_note_pattern_by_name,
    get_rhythm_pattern_by_name
)
from src.note_gen.models.note_sequence import NoteSequence

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/v1/users/me")
async def get_current_user():
    """Get the current user."""
    return {"username": "testuser"}

@router.post("/api/v1/generate-sequence", response_model=NoteSequence)
async def generate_sequence(
    sequence_data: GenerateSequenceRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Generate a note sequence based on provided parameters.
    """
    try:
        # Log the request data
        logger.info(f"Received request to generate sequence with data: {sequence_data.model_dump_json()}")
        
        # Fetch the required presets from the database
        chord_progression = await get_chord_progression_by_name(db, sequence_data.progression_name)
        if not chord_progression:
            logger.warning(f"Chord progression '{sequence_data.progression_name}' not found")
            raise HTTPException(status_code=422, detail=f"Chord progression '{sequence_data.progression_name}' not found")
            
        note_pattern = await get_note_pattern_by_name(db, sequence_data.note_pattern_name)
        if not note_pattern:
            logger.warning(f"Note pattern '{sequence_data.note_pattern_name}' not found")
            raise HTTPException(status_code=422, detail=f"Note pattern '{sequence_data.note_pattern_name}' not found")
            
        rhythm_pattern = await get_rhythm_pattern_by_name(db, sequence_data.rhythm_pattern_name)
        if not rhythm_pattern:
            logger.warning(f"Rhythm pattern '{sequence_data.rhythm_pattern_name}' not found")
            raise HTTPException(status_code=422, detail=f"Rhythm pattern '{sequence_data.rhythm_pattern_name}' not found")
        
        # Generate the sequence
        sequence = await generate_sequence_from_presets(
            progression_name=sequence_data.progression_name,
            note_pattern_name=sequence_data.note_pattern_name,
            rhythm_pattern_name=sequence_data.rhythm_pattern_name,
            scale_info=sequence_data.scale_info,
            chord_progression=chord_progression,
            note_pattern=note_pattern,
            rhythm_pattern=rhythm_pattern
        )
        
        return sequence
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating sequence: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))