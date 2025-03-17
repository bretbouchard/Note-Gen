"""
Note sequence route handlers with improved error handling and logging.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.dependencies import get_db_conn

from src.note_gen.models.request_models import GenerateSequenceRequest
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.patterns import ChordProgression
from src.note_gen.models.note_sequence import NoteSequence, NoteSequenceCreate
from src.note_gen.models.note import Note
from pydantic import ValidationError
from src.note_gen.models.presets import NOTE_PATTERNS

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
    request: GenerateSequenceRequest = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db_conn)
) -> NoteSequence:
    """
    Generate a note sequence based on provided parameters.
    """
    try:
        # Log incoming data structure
        logger.debug(f"Incoming sequence data: {request}")
        
        # Get presets from database
        try:
            # Log what we're searching for
            logger.debug(f"Searching for chord progression with name: {request.progression_name}")
            
            # Try to find the chord progression
            chord_progression = await db.chord_progressions.find_one({"name": request.progression_name})
            if not chord_progression:
                # If not found, try a case-insensitive search with regex
                logger.debug(f"Chord progression not found with exact name, trying case-insensitive search")
                import re
                pattern = re.compile(f"^{re.escape(request.progression_name)}$", re.IGNORECASE)
                chord_progression = await db.chord_progressions.find_one({"name": {"$regex": pattern}})
            
            # If still not found, raise 404
            if not chord_progression:
                # Log available progressions to help debugging
                all_progressions = await db.chord_progressions.find().to_list(length=20)
                progression_names = [p.get("name") for p in all_progressions]
                logger.debug(f"Available chord progressions: {progression_names}")
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chord progression '{request.progression_name}' not found"
                )
            
            logger.debug(f"Found chord progression: {chord_progression}")
            
            # Find the note pattern
            note_pattern = NOTE_PATTERNS.get(request.note_pattern_name)
            if not note_pattern:
                raise HTTPException(status_code=400, detail="Invalid note pattern name")
            logger.debug(f"Found note pattern: {note_pattern}")
            
            # Find the rhythm pattern
            logger.debug(f"Searching for rhythm pattern with name: {request.rhythm_pattern_name}")
            rhythm_pattern = await db.rhythm_patterns.find_one({"name": request.rhythm_pattern_name})
            if not rhythm_pattern:
                # Try case-insensitive search
                import re
                pattern = re.compile(f"^{re.escape(request.rhythm_pattern_name)}$", re.IGNORECASE)
                rhythm_pattern = await db.rhythm_patterns.find_one({"name": {"$regex": pattern}})
            
            if not rhythm_pattern:
                # Log available patterns
                all_patterns = await db.rhythm_patterns.find().to_list(length=20)
                pattern_names = [p.get("name") for p in all_patterns]
                logger.debug(f"Available rhythm patterns: {pattern_names}")
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Rhythm pattern '{request.rhythm_pattern_name}' not found"
                )
                
            logger.debug(f"Found rhythm pattern: {rhythm_pattern}")
            
            # Check if rhythm pattern exists
            logger.debug(f"Searching for rhythm pattern with name: {request.rhythm_pattern_name}")
            rhythm_pattern = await db.rhythm_patterns.find_one({"name": request.rhythm_pattern_name})
            if not rhythm_pattern:
                # Try case-insensitive search
                import re
                pattern = re.compile(f"^{re.escape(request.rhythm_pattern_name)}$", re.IGNORECASE)
                rhythm_pattern = await db.rhythm_patterns.find_one({"name": {"$regex": pattern}})
            
            if not rhythm_pattern:
                # Log available patterns
                all_patterns = await db.rhythm_patterns.find().to_list(length=20)
                pattern_names = [p.get("name") for p in all_patterns]
                logger.debug(f"Available rhythm patterns: {pattern_names}")
                
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Rhythm pattern '{request.rhythm_pattern_name}' not found"
                )
                
            logger.debug(f"Found rhythm pattern: {rhythm_pattern}")
            
            # Validate rhythm pattern
            if not rhythm_pattern.get("pattern"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rhythm pattern must contain a pattern"
                )
            
            # Access scale info directly using dot notation
            root_note_name = request.scale_info.root.note_name
            root_octave = request.scale_info.root.octave
            scale_type = request.scale_info.scale_type

            # Generate sequence from presets
            logger.debug(f"Incoming chord progression data: {chord_progression}")
            logger.debug("Chord Progression Data: %s", chord_progression)
            
            # Add scale_info to the chord_progression before creating the instance
            chord_progression_data = dict(chord_progression)
            chord_progression_data['scale_info'] = request.scale_info
            logger.debug(f"Adding scale_info to chord progression: {request.scale_info}")
            
            chord_progression_instance = ChordProgression(**chord_progression_data)
            
            # Extract chords from the chord progression if not provided in request
            chords_to_use = request.chords
            if chords_to_use is None:
                # Use chords from the chord progression
                chords_to_use = chord_progression_instance.chords
                logger.debug(f"Using chords from progression: {chords_to_use}")
            else:
                logger.debug(f"Using user-provided chords: {chords_to_use}")
                
            sequence = await generate_sequence_from_presets(
                request.progression_name,
                request.note_pattern_name,
                request.rhythm_pattern_name,
                request.scale_info,
                chord_progression_instance,
                note_pattern,
                rhythm_pattern,
                chords_to_use
            )
            
            # Save sequence to database
            # (Saving logic not shown)
            return sequence
        except HTTPException as http_ex:
            # Pass HTTP exceptions through without changing them
            logger.error(f"HTTP exception during sequence generation: {http_ex.detail} (status: {http_ex.status_code})")
            raise http_ex
        except Exception as e:
            # Wrap non-HTTP exceptions in a 500 error
            logger.error(f"Unexpected error in sequence generation: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal error during sequence generation: {str(e)}")
    
    except HTTPException as http_ex:
        # Pass HTTP exceptions through without changing them
        logger.error(f"HTTP exception in outer handler: {http_ex.detail} (status: {http_ex.status_code})")
        raise http_ex
    except Exception as e:
        # Wrap non-HTTP exceptions in a 500 error
        logger.error(f"Unexpected error in outer handler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
        progression_name (str): Name of chord progression
        note_pattern_name (str): Name of note pattern
        rhythm_pattern_name (str): Name of rhythm pattern
        scale_info (ScaleInfo): Scale info
        chord_progression (ChordProgression): Chord progression
        note_pattern (dict): Note pattern data
        rhythm_pattern (dict): Rhythm pattern data
    
    Returns:
        dict: Generated note sequence
    """
    try:
        # Log all the input parameters for debugging
        logger.debug(f"Generate sequence from presets:")
        logger.debug(f"  - Progression: {progression_name}")
        logger.debug(f"  - Note Pattern: {note_pattern_name}")
        logger.debug(f"  - Rhythm Pattern: {rhythm_pattern_name}")
        logger.debug(f"  - Scale: {scale_info.root.note_name} {scale_info.scale_type}")
        
        # Handle both Chord objects and dictionaries for logging
        chord_info = []
        for c in chords:
            if hasattr(c, 'root') and hasattr(c, 'quality'):
                # It's a Chord object
                chord_info.append(f"{c.root.note_name}{c.quality.name if hasattr(c.quality, 'name') else c.quality}")
            elif isinstance(c, dict) and 'root' in c and 'quality' in c:
                # It's a dictionary
                root = c['root']
                root_name = root['note_name'] if isinstance(root, dict) and 'note_name' in root else str(root)
                chord_info.append(f"{root_name}{c['quality']}")
            else:
                chord_info.append(str(c))
                
        logger.debug(f"  - Chords: {chord_info}")
        
        # Get scale notes
        scale_notes = scale_info.get_scale_notes()
        logger.debug(f"Scale notes: {[note.note_name + str(note.octave) for note in scale_notes]}")
        
        # Get the intervals from the pattern
        pattern_data = note_pattern.get("data", {}) if note_pattern else {}
        pattern_intervals = pattern_data.get("intervals", [0, 4, 7])  # default to major triad if not specified
        logger.debug(f"Pattern intervals: {pattern_intervals}")
        
        # Get rhythm pattern notes
        if not rhythm_pattern:
            logger.error("Rhythm pattern is missing")
            raise ValueError("Rhythm pattern is required")
            
        # Ensure pattern field exists (required for validation)
        if "pattern" not in rhythm_pattern:
            logger.error("Rhythm pattern is missing the 'pattern' field which is required")
            raise ValueError("Rhythm pattern must contain a 'pattern' field")
            
        # Get the rhythm notes from data.notes if available, otherwise use pattern field
        rhythm_data_obj = rhythm_pattern.get("data", {})
        if rhythm_data_obj and "notes" in rhythm_data_obj:
            rhythm_data = rhythm_data_obj["notes"]
            logger.debug(f"Using rhythm notes from data.notes: {rhythm_data}")
        else:
            rhythm_data = rhythm_pattern.get("pattern", [])
            logger.debug(f"Using rhythm notes from pattern field: {rhythm_data}")
            
        if not rhythm_data:
            logger.error("No rhythm data found in rhythm pattern")
            raise ValueError("Rhythm pattern must contain notes")
            
        logger.debug(f"Rhythm notes: {rhythm_data}")
        
        # Initialize list of generated notes
        generated_notes = []
        absolute_position = 0.0
        
        for chord_idx, chord in enumerate(chords):
            # Extract chord root and quality
            chord_root = None
            chord_quality = None
            
            # Handle different chord types - could be Chord object or dict
            if hasattr(chord, 'root') and hasattr(chord.root, 'note_name'):
                # It's a Chord object
                chord_root = chord.root.note_name
                chord_quality = chord.quality.name if hasattr(chord.quality, 'name') else chord.quality
                logger.debug(f"Processing Chord object: root={chord_root}, quality={chord_quality}")
            elif isinstance(chord, dict):
                # It's a dictionary
                if "root" in chord and isinstance(chord["root"], dict):
                    root_dict = chord["root"]
                    chord_root = root_dict.get("note_name")
                
                chord_quality = chord.get("quality")
                logger.debug(f"Processing chord dict: root={chord_root}, quality={chord_quality}")
            
            # Skip if we don't have enough information to generate notes
            if not chord_root or not chord_quality:
                logger.warning(f"Skipping chord at index {chord_idx}: Missing root or quality")
                continue
            
            logger.debug(f"Processing chord {chord_idx}: {chord_root} {chord_quality}")
            
            # Find the scale index of the chord root
            root_index = -1
            for i, note in enumerate(scale_notes):
                if note.note_name == chord_root:
                    root_index = i
                    break
            
            if root_index == -1:
                logger.warning(f"Chord root {chord_root} not found in scale - using first scale note")
                root_index = 0
            
            logger.debug(f"Chord root {chord_root} found at scale index {root_index}")
                
            # GENERATE NOTES FROM CHORD
            # For each rhythm note
            for rhythm_note in rhythm_data:
                # Skip rests
                if isinstance(rhythm_note, dict) and rhythm_note.get("is_rest", False):
                    logger.debug(f"Skipping rest in rhythm pattern")
                    continue
                
                # For each interval in the pattern
                for interval_idx, interval in enumerate(pattern_intervals):
                    # Calculate the actual note based on chord position in scale
                    # Treat chord root as starting point and apply the interval
                    scale_size = len(scale_notes)
                    interval_from_root = interval
                    
                    # Calculate the actual position in the scale
                    note_index_in_scale = (root_index + interval_from_root) % scale_size
                    target_note = scale_notes[note_index_in_scale]
                    
                    # Calculate octave adjustments more carefully
                    # If root_index + interval exceeds scale size, we need to increase octave
                    # The number of times we wrap around determines octave adjustment
                    octave_adjustment = (root_index + interval_from_root) // scale_size
                    
                    # Start with the base octave from the scale root
                    base_octave = scale_info.root.octave
                    
                    # Get the octave of the chord root (may be different from scale root octave)
                    chord_root_octave = None
                    
                    # Check for chord octave in different formats
                    if hasattr(chord, 'root') and hasattr(chord.root, 'octave'):
                        # Chord object
                        chord_root_octave = chord.root.octave
                        logger.debug(f"  - Using chord object's octave: {chord_root_octave}")
                    elif isinstance(chord, dict) and isinstance(chord.get("root"), dict) and "octave" in chord["root"]:
                        # Dictionary format
                        chord_root_octave = chord["root"]["octave"]
                        logger.debug(f"  - Using chord dict's octave: {chord_root_octave}")
                    else:
                        # Default to scale root octave if chord doesn't specify
                        chord_root_octave = base_octave
                        logger.debug(f"  - Using scale root octave (default): {chord_root_octave}")
                    
                    # Log detailed calculation steps for the first few notes to aid debugging
                    if chord_idx < 2 and interval_idx < 3:
                        logger.debug(f"Detailed note calculation:")
                        logger.debug(f"  - Chord: {chord_root}{chord_quality} (index {chord_idx})")
                        logger.debug(f"  - Root index in scale: {root_index}")
                        logger.debug(f"  - Interval from pattern: {interval}")
                        logger.debug(f"  - Scale size: {scale_size}")
                        logger.debug(f"  - Target note index: (root_index {root_index} + interval {interval}) % {scale_size} = {note_index_in_scale}")
                        logger.debug(f"  - Target note: {target_note.note_name}")
                        logger.debug(f"  - Octave calculation: floor((root_index {root_index} + interval {interval}) / {scale_size}) = {octave_adjustment}")
                        logger.debug(f"  - Base octave: {base_octave}, Chord root octave: {chord_root_octave}")
                        logger.debug(f"  - Final octave: {chord_root_octave} + {octave_adjustment} = {chord_root_octave + octave_adjustment}")
                    
                    # Final octave is the chord root's octave plus any adjustment from interval
                    final_octave = chord_root_octave + octave_adjustment
                    
                    # Create the note
                    try:
                        duration = rhythm_note.get("duration", 1.0) if isinstance(rhythm_note, dict) else 1.0
                        velocity = rhythm_note.get("velocity", 100) if isinstance(rhythm_note, dict) else 100
                        position = rhythm_note.get("position", 0.0) if isinstance(rhythm_note, dict) else 0.0
                        
                        note = Note(
                            note_name=target_note.note_name,
                            octave=final_octave,
                            duration=duration,
                            velocity=velocity
                        )
                        
                        # For the note sequence, we need to combine rhythm position with 
                        # the absolute position to ensure notes are positioned correctly
                        note_dict = note.to_dict()
                        note_dict["position"] = absolute_position + position
                        
                        generated_notes.append(note_dict)
                        
                        if chord_idx < 2 and interval_idx < 3:
                            logger.debug(f"  - Generated note: {note.note_name}{note.octave} (MIDI: {note.midi_number}) at position {note_dict['position']}")
                    except Exception as note_error:
                        logger.error(f"Error creating note: {note_error}")
                        logger.error(f"Attempted with: note_name={target_note.note_name}, octave={final_octave}")
                        raise
            
            # Update absolute position for the next chord
            # Get chord duration based on chord type
            chord_duration = 4.0  # Default duration
            if hasattr(chord, 'duration') and chord.duration is not None:
                chord_duration = chord.duration
            elif isinstance(chord, dict) and "duration" in chord:
                chord_duration = chord.get("duration", 4.0)
            
            absolute_position += chord_duration
            logger.debug(f"Updated absolute position to {absolute_position} after chord {chord_idx}")
        
        # Create the note sequence response
        response = {
            "progression_name": progression_name,
            "note_pattern_name": note_pattern_name,
            "rhythm_pattern_name": rhythm_pattern_name,
            "notes": generated_notes,
            "key": scale_info.key,
            "scale_type": scale_info.scale_type
        }
        
        logger.debug(f"Generated sequence with {len(generated_notes)} notes")
        return response
    except Exception as e:
        logger.exception(f"Error generating sequence from presets: {e}")
        raise

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
