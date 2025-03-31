from src.note_gen.models.base import BaseModelWithConfig
from src.note_gen.validation.base_validation import ValidationResult
from typing import List, Dict, Any
from src.note_gen.models.rhythm import RhythmNote, RhythmPattern
from src.note_gen.models.pattern_interpreter import PatternInterpreter
from src.note_gen.core.enums import ScaleType
from src.note_gen.models.scale import Scale
from src.note_gen.models.note import Note

def test_rhythm_pattern_interpretation():
    """Test rhythm pattern interpretation with scale."""
    # Create test rhythm notes as RhythmNote objects
    notes = [
        RhythmNote(
            position=0.0,
            duration=1.0,
            velocity=64,
            accent=False
        ),
        RhythmNote(
            position=1.0,
            duration=1.0,
            velocity=64,
            accent=True
        )
    ]

    # Create a scale for the interpreter
    scale = Scale(root=Note(pitch="C", octave=4), scale_type=ScaleType.MAJOR)
    
    # Create pattern
    pattern = RhythmPattern(
        name="Test Pattern",
        pattern=notes,
        time_signature=(4, 4),
        scale_type=ScaleType.MAJOR
    )
    
    # Convert rhythm notes to the format expected by PatternInterpreter
    interpreted_pattern = [
        {
            "position": note.position,
            "duration": note.duration,
            "velocity": note.velocity,
            "accent": note.accent
        } for note in pattern.pattern
    ]
    
    # Create interpreter with the converted pattern
    interpreter = PatternInterpreter(pattern=interpreted_pattern, scale=scale)
    
    # Add assertions to verify the interpretation
    assert len(interpreter.pattern) == 2
    assert all(isinstance(note, dict) for note in interpreter.pattern)
