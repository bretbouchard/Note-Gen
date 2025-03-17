"""
Test data generator for rhythm and note patterns.
Helps create valid test data for database insertion and validation.
"""

import uuid
import math
import random
import logging
from typing import Optional, List, Dict, Union, Any

from src.note_gen.models.note import Note
from src.note_gen.models.patterns import RhythmNote, RhythmPatternData, RhythmPattern
from src.note_gen.models.patterns import NotePattern, NotePatternData

logger = logging.getLogger(__name__)

def generate_rhythm_note(
    position: Optional[float] = None,
    duration: Optional[float] = None,
    velocity: Optional[int] = None,
    is_rest: Optional[bool] = None,
    pitch: Optional[int] = None,
    accent: Optional[float] = None,
    swing_ratio: Optional[float] = None
) -> RhythmNote:
    """Generate a valid RhythmNote with optional custom parameters."""
    # Determine is_rest first
    is_rest = is_rest if is_rest is not None else random.choice([True, False])
    
    # Adjust velocity based on is_rest
    if is_rest:
        # For rest notes, use a default low velocity that passes validation
        velocity = 1
    else:
        # Ensure velocity is always > 0 for non-rest notes
        velocity = max(1, velocity if velocity is not None else random.randint(50, 127))
    
    return RhythmNote(
        position=position if position is not None else round(random.uniform(0.0, 3.9), 2),
        duration=duration if duration is not None else round(random.uniform(0.25, 1.0), 2),
        velocity=velocity,
        is_rest=is_rest,
        pitch=pitch if pitch is not None else random.randint(60, 72) if not is_rest else None,
        accent=accent if accent is not None else round(random.uniform(0.0, 2.0), 2),
        swing_ratio=swing_ratio if swing_ratio is not None else round(random.uniform(0.5, 0.75), 2)
    )

def generate_rhythm_pattern_data(
    notes: Optional[List[RhythmNote]] = None,
    time_signature: Optional[str] = None,
    swing_enabled: Optional[bool] = None,
    total_duration: Optional[float] = None
) -> RhythmPatternData:
    """Generate a valid RhythmPatternData with robust validation and musically meaningful generation."""
    # Validate time signature
    time_signature = time_signature or "4/4"
    try:
        numerator, denominator = map(int, time_signature.split('/'))
        if denominator not in [2, 4, 8, 16] or numerator <= 0:
            raise ValueError(f"Invalid time signature: {time_signature}")
    except ValueError:
        raise ValueError(f"Invalid time signature format: {time_signature}")
    
    # Calculate total duration based on time signature
    total_duration = total_duration or (4.0 * numerator / denominator)
    
    # Generate notes that create a musically meaningful rhythm
    if notes is None:
        notes = []
        current_position = 0.0
        
        # Create a more structured rhythm generation
        beat_division = 0.5  # Subdivide beats into smaller units
        while current_position < total_duration:
            # Vary note durations with more musical patterns
            duration_options = [beat_division, 1.0, 1.5, 2.0]
            duration = random.choice(duration_options)
            
            # Ensure we don't exceed total_duration
            if current_position + duration > total_duration:
                duration = total_duration - current_position
            
            # More intelligent rest generation
            is_rest = random.choices([True, False], weights=[0.2, 0.8])[0]
            
            note = generate_rhythm_note(
                position=current_position, 
                duration=round(duration, 2),
                is_rest=is_rest,
                # Add more structured velocity and accent generation
                velocity=random.randint(60, 100) if not is_rest else 0,
                accent=round(random.uniform(0.5, 1.5), 2) if not is_rest else 0.0
            )
            notes.append(note)
            current_position += duration
    
    # Validate generated notes
    total_generated_duration = sum(note.duration for note in notes)
    if not math.isclose(total_generated_duration, total_duration, rel_tol=1e-2):
        logger.warning("Generated notes duration %s does not match total duration %s", 
                      total_generated_duration, total_duration)
    
    # More intelligent swing and groove generation
    swing_enabled = swing_enabled if swing_enabled is not None else random.choice([True, False])
    swing_ratio = round(random.uniform(0.5, 0.75), 2) if swing_enabled else 0.5
    
    return RhythmPatternData(
        name=f"Test Pattern {str(uuid.uuid4())[:8]}",
        pattern=notes,
        notes=notes,
        time_signature=time_signature,
        swing_enabled=swing_enabled,
        total_duration=total_duration,
        swing_ratio=swing_ratio,
        default_duration=beat_division,  # Use the beat subdivision as default
        groove_type=random.choice(['straight', 'swing', 'shuffle']),
        accent_pattern=[
            round(random.uniform(0.5, 2.0), 2) 
            for _ in range(min(numerator, 4))  # Limit accent pattern to time signature
        ]
    )

def generate_rhythm_pattern(
    pattern: Optional[List[float]] = None,
    name: str = 'Test Rhythm Pattern',
    description: str = 'Automatically generated test rhythm pattern',
    tags: List[str] = ['test', 'generated'],
    data: Optional[Union[RhythmPatternData, Dict[str, Any]]] = None,
    is_test: bool = True
) -> RhythmPattern:
    """Generate a valid RhythmPattern with optional custom parameters."""
    if data is None:
        data = generate_rhythm_pattern_data()
    elif isinstance(data, dict):
        data = RhythmPatternData(**data)

    return RhythmPattern(
        id=str(uuid.uuid4()),
        pattern=pattern,
        name=name,
        description=description,
        tags=tags,
        data=data,
        complexity=round(random.uniform(0.1, 1.0), 2),
        is_test=is_test
    )

def generate_note_pattern(
    name: str = 'Test Note Pattern',
    pattern: List[int] = [0, 2, 4, 7],
    description: str = 'Automatically generated test note pattern',
    tags: List[str] = ['test', 'generated'],
    complexity: float = 0.5,
    direction: str = 'up',
    duration: float = 1.0,
    velocity: int = 100,
    is_test: bool = True,
    arpeggio_mode: bool = False,
    data: Optional[Union[NotePatternData, Dict[str, Any]]] = None,
    index: Optional[int] = None
) -> NotePattern:
    """
    Generate a valid NotePattern with enhanced musical coherence and robust validation.
    
    Args:
        name: Optional name for the note pattern
        pattern: Optional interval pattern
        description: Optional description
        tags: Optional tags
        complexity: Optional complexity rating
        direction: Optional pattern direction
        duration: Optional note duration
        velocity: Optional note velocity
        is_test: Flag to indicate if this is a test pattern
        arpeggio_mode: Flag to indicate arpeggio-style generation
        data: Optional pre-defined note pattern data
        index: Optional index for the pattern
    
    Returns:
        A validated NotePattern instance with musically coherent intervals
    """
    # Predefined interval sets for more musically meaningful patterns
    INTERVAL_SETS = {
        'major_scale': [2, 2, 1, 2, 2, 2, 1],
        'minor_scale': [2, 1, 2, 2, 1, 2, 2],
        'pentatonic': [3, 2, 2, 3, 2],
        'blues': [3, 2, 1, 1, 3, 2]
    }
    
    # Define a list of note names for mapping MIDI numbers
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Generate pattern if not provided
    if pattern is None:
        # Choose a more musically coherent interval set
        chosen_set = random.choice(list(INTERVAL_SETS.keys()))
        pattern = INTERVAL_SETS[chosen_set]
        
        # Randomly decide to use ascending or descending pattern
        if random.choice([True, False]):
            pattern = [-interval for interval in pattern]
    
    # Validate and adjust pattern
    pattern = [int(interval) for interval in pattern]
    
    # Validate direction
    direction = direction or random.choice(['up', 'down', 'random'])
    
    # Set default name if not provided
    name = name or f"Test Note Pattern {str(uuid.uuid4())[:8]}"
    
    # Generate data if not provided
    if data is None:
        data = NotePatternData(
            intervals=pattern,
            direction=direction,
            duration=duration,
            velocity=velocity,
            arpeggio_mode=arpeggio_mode
        )
    elif isinstance(data, dict):
        data = NotePatternData(**data)

    return NotePattern(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        tags=tags,
        complexity=complexity,
        is_test=is_test,
        data=data,
        index=index
    )

def generate_test_note_pattern(
    name: str = 'Test Note Pattern',
    pattern: List[int] = [0, 2, 4, 7],
    description: str = 'Automatically generated test note pattern',
    is_test: bool = True,
    **kwargs: Any
) -> NotePattern:
    return generate_note_pattern(
        name=name,
        pattern=pattern,
        description=description,
        is_test=is_test,
        **kwargs
    )


def generate_test_rhythm_pattern(
    name: str = 'Test Rhythm Pattern',
    description: str = 'Automatically generated test rhythm pattern',
    is_test: bool = True,
    **kwargs: Any
) -> RhythmPattern:
    return RhythmPattern(
        id=str(uuid.uuid4()),
        pattern=[1, 0.5, 0.5, 1],
        name=name,
        description=description,
        tags=["test"],
        complexity=1.0,
        is_test=is_test,
        data=RhythmPatternData(
            name="Test Pattern",
            pattern=[1, 0.5, 0.5, 1],
            notes=[],
            time_signature="4/4",
            swing_enabled=False,
            total_duration=4.0,
            swing_ratio=0.5,
            default_duration=0.5,
            groove_type="straight",
            accent_pattern=[1.0, 1.0, 1.0, 1.0]
        )
    )


def generate_test_data(
    num_rhythm_patterns: int = 5,
    num_note_patterns: int = 5
) -> Dict[str, List[Union[RhythmPattern, NotePattern]]]:
    rhythm_patterns = [
        generate_test_rhythm_pattern() for _ in range(num_rhythm_patterns)
    ]
    note_patterns = [
        generate_test_note_pattern() for _ in range(num_note_patterns)
    ]
    return {
        'rhythm_patterns': rhythm_patterns,
        'note_patterns': note_patterns
    }

if __name__ == "__main__":
    # Example usage and testing
    test_data = generate_test_data()
    logger.info("Generated %s rhythm patterns", len(test_data['rhythm_patterns']))
    logger.info("Generated %s note patterns", len(test_data['note_patterns']))