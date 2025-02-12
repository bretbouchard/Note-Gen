"""
Test data generator for rhythm and note patterns.
Helps create valid test data for database insertion and validation.
"""

import uuid
import math
import random
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from src.note_gen.models.note import Note
from src.note_gen.models.rhythm_pattern import RhythmNote, RhythmPatternData, RhythmPattern
from src.note_gen.models.note_pattern import NotePattern, NotePatternData

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
        logging.warning(f"Generated notes duration {total_generated_duration} does not match total duration {total_duration}")
    
    # More intelligent swing and groove generation
    swing_enabled = swing_enabled if swing_enabled is not None else random.choice([True, False])
    swing_ratio = round(random.uniform(0.5, 0.75), 2) if swing_enabled else 0.5
    
    return RhythmPatternData(
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
    name: str = None,
    description: str = None,
    tags: List[str] = None,
    data: RhythmPatternData = None,
    is_test: bool = True
) -> RhythmPattern:
    """Generate a valid RhythmPattern with optional custom parameters."""
    if data is None:
        data = generate_rhythm_pattern_data()
    
    return RhythmPattern(
        id=str(uuid.uuid4()),
        name=name or f"Test Rhythm Pattern {str(uuid.uuid4())[:8]}",
        description=description or "Automatically generated test rhythm pattern",
        tags=tags or (["test", "generated"] if is_test else []),
        data=data,
        complexity=round(random.uniform(0.1, 1.0), 2),
        is_test=is_test
    )

def generate_note_pattern(
    name: str = None,
    pattern: List[int] = None,
    description: str = None,
    tags: List[str] = None,
    complexity: float = None,
    direction: str = None,
    duration: float = None,
    velocity: int = None,
    is_test: bool = True,
    arpeggio_mode: bool = False,
    data: Optional[Union[NotePatternData, Dict]] = None,
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
    
    # Set default description
    description = description or "Automatically generated test note pattern"
    
    # Set default tags
    tags = tags or (["test", "generated"] if is_test else [])
    
    # Set default complexity
    complexity = complexity or round(random.uniform(0.1, 1.0), 2)
    
    # Set default duration
    duration = duration or round(random.uniform(0.5, 2.0), 2)
    
    # Set default velocity
    velocity = velocity or random.randint(50, 100)
    
    # If index is not provided, generate a default index
    index = index if index is not None else random.randint(1, 100)
    
    # If data is provided, ensure it has an index
    if data is not None:
        if isinstance(data, dict):
            data['index'] = data.get('index', index)
        elif isinstance(data, NotePatternData):
            data.index = data.index if data.index is not None else index
    else:
        # Create a default NotePatternData with the index
        data = NotePatternData(
            notes=[
                {
                    'note_name': 'C',
                    'octave': 4,
                    'midi_number': 60,
                    'duration': duration or 1.0,
                    'velocity': velocity or 64
                }
            ],
            intervals=pattern or [0, 2, 4],
            duration=duration or 1.0,
            index=index
        )
    
    return NotePattern(
        id=str(uuid.uuid4()),
        name=name,
        pattern=pattern,
        description=description,
        tags=tags,
        complexity=complexity,
        is_test=is_test,
        direction=direction,
        duration=duration,
        velocity=velocity,
        data=data,
        index=index
    )

def generate_test_data(
    num_rhythm_patterns: int = 5, 
    num_note_patterns: int = 5
) -> Dict[str, List[Union[RhythmPattern, NotePattern]]]:
    """
    Generate comprehensive test data for rhythm and note patterns.
    
    Args:
        num_rhythm_patterns: Number of rhythm patterns to generate
        num_note_patterns: Number of note patterns to generate
    
    Returns:
        Dictionary containing lists of generated rhythm and note patterns
    """
    # Generate rhythm patterns with careful validation
    rhythm_patterns = []
    for i in range(num_rhythm_patterns):
        try:
            rhythm_pattern = generate_rhythm_pattern(
                name=f"Test Rhythm Pattern {i+1}",
                description=f"Automatically generated test rhythm pattern {i+1}",
                is_test=True,
                data=generate_rhythm_pattern_data(
                    time_signature="4/4",
                    swing_enabled=False,  # Consistent swing setting
                    total_duration=4.0
                )
            )
            rhythm_patterns.append(rhythm_pattern)
        except Exception as e:
            logging.error(f"Failed to generate rhythm pattern: {e}")
    
    # Generate note patterns with careful validation
    note_patterns = []
    predefined_patterns = [
        [0, 2, 4],    # Major triad
        [0, 3, 7],    # Minor triad
        [0, 4, 7],    # Major triad
        [0, 3, 6],    # Diminished triad
        [0, 4, 8]     # Augmented triad
    ]
    
    for i in range(num_note_patterns):
        try:
            # Use predefined patterns to ensure consistency
            pattern = predefined_patterns[i % len(predefined_patterns)]
            
            note_pattern = generate_note_pattern(
                name=f"Test Note Pattern {i+1}",
                pattern=pattern,
                description=f"Automatically generated test note pattern {i+1}",
                direction='forward',
                complexity=round(0.5, 2),  # Consistent complexity
                is_test=True,
                tags=['test', 'generated'],
                index=i
            )
            
            # Ensure the note pattern passes validation
            if note_pattern and note_pattern.data:
                note_patterns.append(note_pattern)
        except Exception as e:
            logging.error(f"Failed to generate note pattern: {e}")
    
    # Ensure we have at least one valid pattern of each type
    if not rhythm_patterns:
        rhythm_patterns.append(
            generate_rhythm_pattern(
                name="Default Rhythm Pattern",
                description="Fallback rhythm pattern for testing",
                is_test=True
            )
        )
    
    if not note_patterns:
        note_patterns.append(
            generate_note_pattern(
                name="Default Note Pattern",
                description="Fallback note pattern for testing",
                is_test=True
            )
        )
    
    return {
        'rhythm_patterns': rhythm_patterns,
        'note_patterns': note_patterns
    }

def generate_test_note_pattern(
    name: Optional[str] = None,
    pattern: Optional[List[int]] = None,
    description: Optional[str] = None,
    is_test: bool = True,
    **kwargs
) -> NotePattern:
    """
    Generate a test note pattern with robust validation and default values.
    
    Args:
        name: Optional name for the note pattern
        pattern: Optional interval pattern
        description: Optional description
        is_test: Flag to indicate if this is a test pattern
        **kwargs: Additional parameters to pass to generate_note_pattern
    
    Returns:
        A validated NotePattern instance
    """
    # Set default pattern if not provided
    if pattern is None:
        pattern = [0, 2, 4]  # Default major triad intervals
    
    # Set default name
    if name is None:
        name = f"Test Note Pattern {str(uuid.uuid4())[:8]}"
    
    # Set default description
    if description is None:
        description = "Automatically generated test note pattern"
    
    # Merge additional parameters
    generation_params = {
        'name': name,
        'pattern': pattern,
        'description': description,
        'is_test': is_test,
        'tags': ['test', 'generated']
    }
    generation_params.update(kwargs)
    
    # Generate note pattern
    note_pattern = generate_note_pattern(**generation_params)
    
    return note_pattern

def generate_test_rhythm_pattern(
    name: Optional[str] = None,
    pattern: Optional[List[float]] = None,
    description: Optional[str] = None,
    is_test: bool = True,
    **kwargs
) -> RhythmPattern:
    """
    Generate a test rhythm pattern with robust validation and default values.
    
    Args:
        name: Optional name for the rhythm pattern
        pattern: Optional rhythm pattern
        description: Optional description
        is_test: Flag to indicate if this is a test pattern
        **kwargs: Additional parameters to pass to generate_rhythm_pattern
    
    Returns:
        A validated RhythmPattern instance
    """
    # Set default pattern if not provided
    if pattern is None:
        pattern = [1.0, 0.5, 0.5]  # Default quarter, eighth, eighth
    
    # Set default name
    if name is None:
        name = f"Test Rhythm Pattern {str(uuid.uuid4())[:8]}"
    
    # Set default description
    if description is None:
        description = "Automatically generated test rhythm pattern"
    
    # Merge additional parameters
    generation_params = {
        'name': name,
        'pattern': pattern,
        'description': description,
        'is_test': is_test,
        'tags': ['test', 'generated']
    }
    generation_params.update(kwargs)
    
    # Generate rhythm pattern
    rhythm_pattern = generate_rhythm_pattern(**generation_params)
    
    return rhythm_pattern

if __name__ == "__main__":
    # Example usage and testing
    test_data = generate_test_data()
    
    print("Generated Rhythm Patterns:")
    for pattern in test_data['rhythm_patterns']:
        print(f"- {pattern.name}")
    
    print("\nGenerated Note Patterns:")
    for pattern in test_data['note_patterns']:
        print(f"- {pattern.name}")
