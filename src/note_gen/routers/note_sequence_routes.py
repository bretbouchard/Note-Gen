"""
Note sequence route handlers with improved error handling and logging.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.note_sequence import NoteSequence, NoteSequenceCreate
from src.note_gen.models.request_models import GenerateSequenceRequest
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord_progression import ChordProgression
from pydantic import ValidationError

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["note-sequences"]
)

def _validate_note_sequence(sequence: NoteSequence):
    """
    Validate note sequence with comprehensive checks.
    
    Args:
        sequence (NoteSequence): Note sequence to validate
    
    Raises:
        ValueError: If validation fails
    """
    # Add validation logic specific to note sequences
    if not sequence.notes or len(sequence.notes) == 0:
        raise ValueError("Note sequence must contain at least one note")

@router.get("/", response_model=List[NoteSequence])
async def get_note_sequences(
    db: AsyncIOMotorDatabase = Depends(get_db_conn),
    limit: int = 100
) -> List[NoteSequence]:
    """
    Retrieve all note sequences from the database.
    
    Args:
        db (AsyncIOMotorDatabase): Database connection
        limit (int, optional): Maximum number of sequences to retrieve. Defaults to 100.
    
    Returns:
        List[NoteSequence]: List of note sequences
    """
    try:
        cursor = db.note_sequences.find().limit(limit)
        sequences = await cursor.to_list(length=limit)
        return [NoteSequence(**sequence) for sequence in sequences]
    except Exception as e:
        logger.error(f"Error retrieving note sequences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve note sequences"
        )

@router.get("/{sequence_id}", response_model=NoteSequence)
async def get_note_sequence(
    sequence_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NoteSequence:
    """
    Retrieve a specific note sequence by its ID.
    
    Args:
        sequence_id (str): The unique identifier of the note sequence
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        NoteSequence: The requested note sequence
    
    Raises:
        HTTPException: If the note sequence is not found
    """
    try:
        sequence = await db.note_sequences.find_one({"_id": sequence_id})
        if not sequence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note sequence {sequence_id} not found"
            )
        return NoteSequence(**sequence)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving note sequence {sequence_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve note sequence {sequence_id}"
        )

@router.post("/", response_model=NoteSequence)
async def create_note_sequence(
    sequence: NoteSequenceCreate, 
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NoteSequence:
    """
    Create a new note sequence.
    
    Args:
        sequence (NoteSequenceCreate): The note sequence to create
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        NoteSequence: The created note sequence
    
    Raises:
        HTTPException: If there's an error during creation
    """
    try:
        # Validate the sequence
        _validate_note_sequence(sequence)
        
        # Insert the sequence
        result = await db.note_sequences.insert_one(sequence.dict())
        
        # Retrieve the created sequence
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
    except Exception as e:
        logger.error(f"Error creating note sequence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note sequence"
        )

@router.post("/generate-sequence", response_model=NoteSequence)
async def generate_sequence(
    sequence_data: GenerateSequenceRequest,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NoteSequence:
    """
    Generate a note sequence based on provided parameters.
    """
    try:
        # Log incoming data structure
        logger.debug(f"Incoming sequence data: {sequence_data}")
        
        # Get presets from database
        chord_progression = await db.chord_progressions.find_one({"name": sequence_data.progression_name})
        if not chord_progression:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chord progression '{sequence_data.progression_name}' not found"
            )
        
        note_pattern = await db.note_patterns.find_one({"name": sequence_data.note_pattern_name})
        if not note_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note pattern '{sequence_data.note_pattern_name}' not found"
            )
        
        rhythm_pattern = await db.rhythm_patterns.find_one({"name": sequence_data.rhythm_pattern_name})
        if not rhythm_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rhythm pattern '{sequence_data.rhythm_pattern_name}' not found"
            )
        
        # Access scale info directly using dot notation
        root_note_name = sequence_data.scale_info.root.note_name
        root_octave = sequence_data.scale_info.root.octave
        scale_type = sequence_data.scale_info.scale_type

        # Generate sequence from presets
        logger.debug(f"Incoming chord progression data: {chord_progression}")
        logger.debug("Chord Progression Data: %s", chord_progression)
        chord_progression_instance = ChordProgression(**chord_progression)
        sequence = await generate_sequence_from_presets(
            sequence_data.progression_name,
            sequence_data.note_pattern_name,
            sequence_data.rhythm_pattern_name,
            sequence_data.scale_info,
            chord_progression_instance,
            note_pattern,
            rhythm_pattern,
            sequence_data.chords
        )
        
        # Save sequence to database
        # (Saving logic not shown)
        return sequence
    except Exception as e:
        logger.error(f"Error generating note sequence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
    chord_progression: ChordProgression,
    note_pattern: dict,
    rhythm_pattern: dict,
    chords: List[dict]
) -> NoteSequence:
    """
    Generate a note sequence from presets.
    
    Args:
        progression_name (str): Name of the chord progression
        note_pattern_name (str): Name of the note pattern
        rhythm_pattern_name (str): Name of the rhythm pattern
        scale_info (ScaleInfo): Scale information
        chord_progression (ChordProgression): Chord progression details
        note_pattern (dict): Note pattern details
        rhythm_pattern (dict): Rhythm pattern details
        chords (List[dict]): Chords with root and quality
    
    Returns:
        NoteSequence: Generated note sequence
    """
    try:
        # Generate notes based on the chord progression and patterns
        generated_notes = []
        pattern_intervals = note_pattern["data"]["intervals"]
        rhythm_notes = rhythm_pattern["data"]["notes"]
        
        # For each chord in the progression
        for chord_idx, chord in enumerate(chords):
            # For each rhythm note
            for rhythm_note in rhythm_notes:
                # Skip rests
                if rhythm_note.get("is_rest", False):
                    continue
                    
                # For each interval in the pattern
                for interval in pattern_intervals:
                    # Calculate the actual note
                    base_note = chord["root"]
                    note_interval = interval
                    
                    # Create the note
                    note = Note(
                        note_name=base_note,
                        octave=scale_info.root.octave + (note_interval // 12),
                        duration=rhythm_note["duration"],
                        velocity=rhythm_note["velocity"]
                    )
                    generated_notes.append(note)
        
        # Create and return the sequence
        generated_sequence = NoteSequence(
            name=f"Generated Sequence: {progression_name}",
            notes=generated_notes,
            progression_name=progression_name,
            note_pattern_name=note_pattern_name,
            rhythm_pattern_name=rhythm_pattern_name,
            is_test=True
        )
        
        return generated_sequence
    
    except Exception as e:
        logger.error(f"Error in sequence generation: {e}", exc_info=True)
        raise ValueError(f"Failed to generate sequence: {e}")

@router.delete("/{sequence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_sequence(
    sequence_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
):
    """
    Delete a note sequence by its ID.
    
    Args:
        sequence_id (str): The unique identifier of the note sequence
        db (AsyncIOMotorDatabase): Database connection
    
    Raises:
        HTTPException: If the note sequence is not found or if there's an error during deletion
    """
    try:
        result = await db.note_sequences.delete_one({"_id": sequence_id})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note sequence {sequence_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note sequence {sequence_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete note sequence {sequence_id}"
        )

# Example usage
request_data = {
    "progression_name": "I-IV-V-I",
    "note_pattern_name": "Simple Triad",
    "rhythm_pattern_name": "quarter_notes",
    "scale_info": {
        "root": {
            "note_name": "C",
            "octave": 4
        },
        "scale_type": "MAJOR"
    },
    "chords": [
        {"root": "C", "quality": "MAJOR"},
        {"root": "F", "quality": "MAJOR"},
        {"root": "G", "quality": "MAJOR"},
        {"root": "C", "quality": "MAJOR"}
    ]
}
