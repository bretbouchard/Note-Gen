"""
Note sequence route handlers with improved error handling and logging.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.note_gen.database import MongoDBConnection
from src.note_gen.dependencies import get_db_conn
from src.note_gen.models.note_sequence import NoteSequence
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
    conn: MongoDBConnection = Depends(get_db_conn),
    limit: int = 100
) -> List[NoteSequence]:
    """
    Retrieve all note sequences from the database.
    
    Args:
        conn (MongoDBConnection): Database connection
        limit (int, optional): Maximum number of sequences to retrieve. Defaults to 100.
    
    Returns:
        List[NoteSequence]: List of note sequences
    """
    try:
        cursor = conn.db.note_sequences.find().limit(limit)
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
    conn: MongoDBConnection = Depends(get_db_conn)
) -> NoteSequence:
    """
    Retrieve a specific note sequence by its ID.
    
    Args:
        sequence_id (str): The unique identifier of the note sequence
        conn (MongoDBConnection): Database connection
    
    Returns:
        NoteSequence: The requested note sequence
    
    Raises:
        HTTPException: If the note sequence is not found
    """
    try:
        sequence = await conn.db.note_sequences.find_one({"_id": sequence_id})
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
    sequence: NoteSequence, 
    conn: MongoDBConnection = Depends(get_db_conn)
) -> NoteSequence:
    """
    Create a new note sequence with comprehensive validation.
    
    Args:
        sequence (NoteSequence): The note sequence to create
        conn (MongoDBConnection): Database connection
    
    Returns:
        NoteSequence: Created note sequence with assigned ID
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        sequence_dict = sequence.dict()
        result = await conn.db.note_sequences.insert_one(sequence_dict)
        sequence_dict["_id"] = str(result.inserted_id)
        return NoteSequence(**sequence_dict)
    except ValidationError as e:
        logger.error(f"Validation error creating note sequence: {str(e)}")
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

@router.post("/generate", response_model=NoteSequence)
async def generate_sequence(
    sequence_data: GenerateSequenceRequest,
    conn: MongoDBConnection = Depends(get_db_conn)
) -> NoteSequence:
    """
    Generate a note sequence using presets.
    """
    try:
        # Get chord progression
        chord_progression = await conn.db.chord_progressions.find_one(
            {"name": sequence_data.progression_name}
        )
        if not chord_progression:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chord progression {sequence_data.progression_name} not found"
            )

        # Get note pattern
        note_pattern = await conn.db.note_patterns.find_one(
            {"name": sequence_data.note_pattern_name}
        )
        if not note_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note pattern {sequence_data.note_pattern_name} not found"
            )

        # Get rhythm pattern
        rhythm_pattern = await conn.db.rhythm_patterns.find_one(
            {"name": sequence_data.rhythm_pattern_name}
        )
        if not rhythm_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rhythm pattern {sequence_data.rhythm_pattern_name} not found"
            )

        # Generate sequence
        sequence = await generate_sequence_from_presets(
            progression_name=sequence_data.progression_name,
            note_pattern_name=sequence_data.note_pattern_name,
            rhythm_pattern_name=sequence_data.rhythm_pattern_name,
            scale_info=sequence_data.scale_info,
            chord_progression=ChordProgression(**chord_progression),
            note_pattern=note_pattern,
            rhythm_pattern=rhythm_pattern
        )

        # Save sequence
        sequence_dict = sequence.dict()
        result = await conn.db.note_sequences.insert_one(sequence_dict)
        sequence_dict["_id"] = str(result.inserted_id)
        return NoteSequence(**sequence_dict)

    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Validation error generating sequence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating sequence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate sequence"
        )

async def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
    chord_progression: ChordProgression,
    note_pattern: dict,
    rhythm_pattern: dict
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
    
    Returns:
        NoteSequence: Generated note sequence
    """
    try:
        # Generate notes based on the chord progression and patterns
        generated_notes = []
        pattern_intervals = note_pattern["data"]["intervals"]
        rhythm_notes = rhythm_pattern["data"]["notes"]
        
        # For each chord in the progression
        for chord_idx, chord in enumerate(chord_progression.chords):
            # For each rhythm note
            for rhythm_note in rhythm_notes:
                # Skip rests
                if rhythm_note.get("is_rest", False):
                    continue
                    
                # For each interval in the pattern
                for interval in pattern_intervals:
                    # Calculate the actual note
                    base_note = chord.root
                    note_interval = interval
                    
                    # Create the note
                    note = Note(
                        note_name=base_note.note_name,
                        octave=base_note.octave + (note_interval // 12),
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

@router.delete("/{sequence_id}")
async def delete_note_sequence(
    sequence_id: str,
    conn: MongoDBConnection = Depends(get_db_conn)
) -> dict:
    """
    Delete a note sequence by its ID.
    
    Args:
        sequence_id (str): The unique identifier of the note sequence
        conn (MongoDBConnection): Database connection
    
    Raises:
        HTTPException: If the note sequence is not found or if there's an error during deletion
    """
    try:
        result = await conn.db.note_sequences.delete_one({"_id": sequence_id})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note sequence {sequence_id} not found"
            )
        return {"message": f"Note sequence {sequence_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note sequence {sequence_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete note sequence {sequence_id}"
        )
