import pytest
import math
from pydantic import BaseModel, ValidationError, field_validator
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType
from typing import List, Dict, Any, Tuple
import unittest

def test_type_safety():
    """Test type safety."""
    with pytest.raises(ValidationError) as cm:
        RhythmPattern(
            name="Test Pattern",
            pattern=[
                RhythmNote(
                    position=0.0,
                    duration=0.5,
                    velocity=128,  # This will trigger the validation error
                    accent=False,
                    tuplet_ratio=(1, 1),
                    groove_offset=0.0,
                    groove_velocity=1.0
                )
            ],
            time_signature=(2, 4),  # Changed from string to tuple
            description="Type Safety Test"
        )
    assert "Input should be less than or equal to 127" in str(cm.value)

def test_validate_note_pattern():
    """Test note pattern validation."""
    pattern_data = NotePatternData(
        scale_type=ScaleType.MAJOR,
        key="C4",
        max_interval_jump=12,
        allow_chromatic=False
    )
    
    with pytest.raises(ValidationError):
        NotePattern(
            pattern=[
                Note(note_name="C", octave=4, duration=1.0, position=0.0, velocity=64),
                Note(note_name="E", octave=4, duration=1.0, position=1.0, velocity=64),
                Note(note_name="G", octave=4, duration=1.0, position=2.0, velocity=64)
            ],
            time_signature=(4, 4),
            data=pattern_data
        )

def test_validate_rhythm_pattern():
    """Test rhythm pattern validation."""
    pattern = RhythmPattern(
        name="Basic Pattern",
        pattern=[
            RhythmNote(position=0.0, duration=0.5, velocity=64)
        ],
        time_signature=(4, 4),  # Changed from string to tuple
        description="Test Pattern"
    )
    assert len(pattern.pattern) == 1
    assert pattern.time_signature == (4, 4)  # Updated assertion to match tuple format
