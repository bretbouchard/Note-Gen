"""
src/note_gen/routers/user_routes.py

User-related route handlers.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from src.note_gen.models.user import User
from src.note_gen.database import MongoDBConnection
from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.request_models import GenerateSequenceRequest
from src.note_gen.generators.note_sequence_generator import generate_sequence_from_presets
from src.note_gen.models.note_sequence import NoteSequence
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/v1/users/me")
async def get_current_user():
    """Get the current user."""
    return {"username": "testuser"}

@router.get("/users/", response_model=List[User])
async def get_users(conn: MongoDBConnection = Depends(get_db_conn)):
    """Get all users."""
    cursor = conn.db.users.find({})
    return await cursor.to_list(length=100)

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, conn: MongoDBConnection = Depends(get_db_conn)):
    """Get a specific user by ID."""
    user = await conn.db.users.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/", response_model=User, status_code=201)
async def create_user(user: User, conn: MongoDBConnection = Depends(get_db_conn)):
    """Create a new user."""
    result = await conn.db.users.insert_one(user.dict())
    user.id = str(result.inserted_id)
    return user

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str, conn: MongoDBConnection = Depends(get_db_conn)):
    """Delete a user."""
    result = await conn.db.users.delete_one({"_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/api/v1/generate-sequence", response_model=NoteSequence)
async def generate_sequence(
    sequence_data: GenerateSequenceRequest,
    conn: MongoDBConnection = Depends(get_db_conn)
):
    """
    Generate a note sequence based on provided parameters.
    """
    try:
        # Log the request data
        logger.info(f"Received request to generate sequence with data: {sequence_data.model_dump_json()}")
        
        # Fetch the required presets from the database
        chord_progression = await conn.db.chord_progressions.find_one({"name": sequence_data.progression_name})
        if not chord_progression:
            logger.warning(f"Chord progression '{sequence_data.progression_name}' not found")
            raise HTTPException(status_code=422, detail=f"Chord progression '{sequence_data.progression_name}' not found")
            
        note_pattern = await conn.db.note_patterns.find_one({"name": sequence_data.note_pattern_name})
        if not note_pattern:
            logger.warning(f"Note pattern '{sequence_data.note_pattern_name}' not found")
            raise HTTPException(status_code=422, detail=f"Note pattern '{sequence_data.note_pattern_name}' not found")
            
        rhythm_pattern = await conn.db.rhythm_patterns.find_one({"name": sequence_data.rhythm_pattern_name})
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