"""
Note sequence route handlers with improved error handling and logging.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from src.note_gen.dependencies import get_db
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.request_models import GenerateSequenceRequest
from src.note_gen.models.scale_info import ScaleInfo

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/note-sequences",
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
    db: AsyncIOMotorDatabase = Depends(get_db),
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
        logger.info(f"Fetching note sequences (limit: {limit})")
        
        cursor = db.note_sequences.find().limit(limit)
        sequences = await cursor.to_list(length=limit)
        
        note_sequences = [NoteSequence(**sequence) for sequence in sequences]
        
        logger.info(f"Retrieved {len(note_sequences)} note sequences")
        return note_sequences
    
    except Exception as e:
        logger.error(f"Error retrieving note sequences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unable to retrieve note sequences"
        )

@router.get("/{sequence_id}", response_model=NoteSequence)
async def get_note_sequence(
    sequence_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
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
        logger.info(f"Fetching note sequence with ID: {sequence_id}")
        
        sequence = await db.note_sequences.find_one({"_id": sequence_id})
        
        if not sequence:
            logger.warning(f"Note sequence not found with ID: {sequence_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Note sequence with ID {sequence_id} not found"
            )
        
        note_sequence = NoteSequence(**sequence)
        
        logger.info(f"Successfully retrieved note sequence: {sequence_id}")
        return note_sequence
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving note sequence {sequence_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error while fetching note sequence"
        )

@router.post("/", response_model=NoteSequence, status_code=status.HTTP_201_CREATED)
async def create_note_sequence(
    sequence: NoteSequence, 
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> NoteSequence:
    """
    Create a new note sequence with comprehensive validation.
    
    Args:
        sequence (NoteSequence): The note sequence to create
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        NoteSequence: Created note sequence with assigned ID
    
    Raises:
        HTTPException: For various validation and database-related errors
    """
    try:
        logger.info(f"Attempting to create note sequence")
        
        # Validate note sequence
        _validate_note_sequence(sequence)
        
        # Prepare sequence for database insertion
        sequence_dict = sequence.model_dump(by_alias=True)
        
        # Insert into database
        result = await db.note_sequences.insert_one(sequence_dict)
        sequence_dict["id"] = str(result.inserted_id)
        
        # Create and return response
        created_sequence = NoteSequence(**sequence_dict)
        logger.info(f"Successfully created note sequence with ID: {created_sequence.id}")
        return created_sequence
    
    except ValueError as ve:
        logger.error(f"Validation error during note sequence creation: {ve}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error during note sequence creation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during note sequence creation"
        )

@router.post("/generate", response_model=NoteSequence)
async def generate_sequence(
    sequence_data: GenerateSequenceRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> NoteSequence:
    """
    Generate a note sequence based on provided parameters.
    
    Args:
        sequence_data (GenerateSequenceRequest): Parameters for sequence generation
        db (AsyncIOMotorDatabase): Database connection
    
    Returns:
        NoteSequence: Generated note sequence
    
    Raises:
        HTTPException: If required presets are not found or generation fails
    """
    try:
        # Log the request data
        logger.info(f"Received request to generate sequence with data: {sequence_data.model_dump_json()}")
        
        # Fetch the required presets from the database
        chord_progression = await db.chord_progressions.find_one({"name": sequence_data.progression_name})
        if not chord_progression:
            logger.warning(f"Chord progression '{sequence_data.progression_name}' not found")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"Chord progression '{sequence_data.progression_name}' not found"
            )
            
        note_pattern = await db.note_patterns.find_one({"name": sequence_data.note_pattern_name})
        if not note_pattern:
            logger.warning(f"Note pattern '{sequence_data.note_pattern_name}' not found")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"Note pattern '{sequence_data.note_pattern_name}' not found"
            )
            
        rhythm_pattern = await db.rhythm_patterns.find_one({"name": sequence_data.rhythm_pattern_name})
        if not rhythm_pattern:
            logger.warning(f"Rhythm pattern '{sequence_data.rhythm_pattern_name}' not found")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"Rhythm pattern '{sequence_data.rhythm_pattern_name}' not found"
            )
        
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
        
        logger.info(f"Successfully generated note sequence")
        return sequence
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating note sequence: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error during note sequence generation"
        )

async def generate_sequence_from_presets(
    progression_name: str,
    note_pattern_name: str,
    rhythm_pattern_name: str,
    scale_info: ScaleInfo,
    chord_progression: dict,
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
        chord_progression (dict): Chord progression details
        note_pattern (dict): Note pattern details
        rhythm_pattern (dict): Rhythm pattern details
    
    Returns:
        NoteSequence: Generated note sequence
    """
    try:
        logger.info(f"Generating sequence from presets: {progression_name}, {note_pattern_name}, {rhythm_pattern_name}")
        
        # Placeholder for actual sequence generation logic
        # This would typically involve:
        # 1. Interpreting chord progression
        # 2. Applying note pattern
        # 3. Applying rhythm pattern
        # 4. Generating actual notes based on scale info
        
        # Temporary implementation for demonstration
        generated_sequence = NoteSequence(
            name=f"Generated Sequence: {progression_name}",
            notes=[],  # Actual note generation would happen here
            progression_name=progression_name,
            note_pattern_name=note_pattern_name,
            rhythm_pattern_name=rhythm_pattern_name
        )
        
        logger.info("Sequence generation complete")
        return generated_sequence
    
    except Exception as e:
        logger.error(f"Error in sequence generation: {e}", exc_info=True)
        raise ValueError(f"Failed to generate sequence: {e}")
