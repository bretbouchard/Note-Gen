"""
Note sequence route handlers with improved error handling and logging.
"""

import logging
from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.request_models import GenerateSequenceRequest  # Use relative import
from ..models.sequence import NoteSequence, NoteSequenceCreate
from ..core.sequence_generator import generate_sequence_from_presets
from ..core.database import get_db_conn
from ..models.patterns import Pattern  # Use relative import
from ..validation.exceptions import ValidationError
from ..core.enums import ValidationLevel  # Use relative import

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["sequences"]
)

DbDep = Annotated[AsyncIOMotorDatabase, Depends(get_db_conn)]

def _validate_note_sequence(sequence: NoteSequenceCreate) -> None:
    """Validate note sequence data."""
    if not sequence.notes:
        raise ValidationError("Sequence must contain at least one note")
    if sequence.duration <= 0:
        raise ValidationError("Sequence duration must be positive")
    # Add any other validation rules as needed

@router.post("/", response_model=NoteSequence)
async def create_sequence(
    sequence: NoteSequenceCreate,
    db: DbDep
) -> NoteSequence:
    """Create a new note sequence."""
    try:
        _validate_note_sequence(sequence)
        result = await db.note_sequences.insert_one(sequence.dict())
        created_sequence = await db.note_sequences.find_one({"_id": result.inserted_id})
        if not created_sequence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Created sequence not found"
            )
        return NoteSequence(**created_sequence)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.post("/generate", response_model=Pattern)
async def generate_sequence(
    request: GenerateSequenceRequest = Body(...)
) -> Pattern:
    """Generate a new sequence based on provided parameters."""
    try:
        if not request.scale_info:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Scale info is required"
            )
            
        sequence = await generate_sequence_from_presets(
            progression_name=request.progression_name,
            scale_info=request.scale_info,
            time_signature=request.time_signature,
            tempo=request.tempo,
            key=request.key
        )
        return sequence
    except Exception as e:
        logger.error(f"Error generating sequence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{sequence_id}", response_model=NoteSequence)
async def get_sequence(
    sequence_id: str,
    db: DbDep
) -> NoteSequence:
    """Get a specific sequence by ID."""
    sequence = await db.note_sequences.find_one({"_id": sequence_id})
    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )
    return NoteSequence(**sequence)

@router.get("/", response_model=List[NoteSequence])
async def list_sequences(
    db: DbDep
) -> List[NoteSequence]:
    """Get all sequences."""
    sequences = await db.note_sequences.find().to_list(None)
    return [NoteSequence(**sequence) for sequence in sequences]
