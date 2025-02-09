"""
src/note_gen/routes/note_sequences.py

Note sequence route handlers.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.request_models import GenerateSequenceRequest
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1",
    tags=["note-sequences"]
)

# Get all note sequences
@router.get("/note-sequences", response_model=List[NoteSequence])
async def get_note_sequences(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[NoteSequence]:
    """Get all note sequences."""
    try:
        cursor = db.note_sequences.find()
        sequences = await cursor.to_list(length=100)
        return [NoteSequence(**sequence) for sequence in sequences]
    except Exception as e:
        logger.error(f"Error getting note sequences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get a single note sequence by ID
@router.get("/note-sequences/{sequence_id}", response_model=NoteSequence)
async def get_note_sequence(sequence_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> NoteSequence:
    """Get a note sequence by ID."""
    try:
        sequence = await db.note_sequences.find_one({"_id": sequence_id})
        if not sequence:
            raise HTTPException(status_code=404, detail=f"Note sequence {sequence_id} not found")
        return NoteSequence(**sequence)
    except Exception as e:
        logger.error(f"Error getting note sequence {sequence_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Create a new note sequence
@router.post("/note-sequences", response_model=NoteSequence)
async def create_note_sequence(sequence: NoteSequence, db: AsyncIOMotorDatabase = Depends(get_db)) -> NoteSequence:
    """Create a new note sequence."""
    try:
        sequence_dict = sequence.model_dump()
        result = await db.note_sequences.insert_one(sequence_dict)
        sequence_dict["_id"] = str(result.inserted_id)
        return NoteSequence(**sequence_dict)
    except Exception as e:
        logger.error(f"Error creating note sequence: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Generate a note sequence from presets
@router.post("/generate-sequence", response_model=NoteSequence)
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
        chord_progression = await db.chord_progressions.find_one({"name": sequence_data.progression_name})
        if not chord_progression:
            logger.warning(f"Chord progression '{sequence_data.progression_name}' not found")
            raise HTTPException(status_code=422, detail=f"Chord progression '{sequence_data.progression_name}' not found")
            
        note_pattern = await db.note_patterns.find_one({"name": sequence_data.note_pattern_name})
        if not note_pattern:
            logger.warning(f"Note pattern '{sequence_data.note_pattern_name}' not found")
            raise HTTPException(status_code=422, detail=f"Note pattern '{sequence_data.note_pattern_name}' not found")
            
        rhythm_pattern = await db.rhythm_patterns.find_one({"name": sequence_data.rhythm_pattern_name})
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

async def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
) -> NoteSequence:
    """
    Generate a note sequence from presets.
    """
    # Fetch the chord progression, note pattern, and rhythm pattern from the database
    chord_progression = await fetch_chord_progression(progression_name)
    note_pattern = await fetch_note_pattern(note_pattern_name)
    rhythm_pattern = await fetch_rhythm_pattern(rhythm_pattern_name)

    # Create an instance of NoteSequenceGenerator
    generator = NoteSequenceGenerator(
        chord_progression=chord_progression,
        rhythm_pattern=rhythm_pattern
    )

    # Generate the note sequence
    return generator.generate()