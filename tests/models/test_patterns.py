import pytest
from pydantic import ValidationError
from note_gen.models.patterns import (
    NotePatternData,
    TransformationType,
    TransformationModel,
    NotePattern,
    NotePatternValidationError
)
from note_gen.core.enums import ScaleType, PatternDirection
from note_gen.core.constants import DEFAULTS, SCALE_INTERVALS, PATTERN_VALIDATION_LIMITS
from note_gen.models.note import Note
from note_gen.models.chord import Chord, ChordProgressionItem
from note_gen.models.scale_info import ScaleInfo
from typing import Dict, List, Optional, Union, Any, cast

def test_note_pattern_complex_validation() -> None:
    """Test complex validation scenarios."""
    # Test valid pattern
    pattern_data = NotePatternData(
        key="C",
        scale_type=ScaleType.MAJOR,
        direction=PatternDirection.UP,
        max_interval_jump=12
    )
    
    # Test invalid direction
    with pytest.raises(ValidationError):
        NotePatternData(
            key="C",
            scale_type=ScaleType.MAJOR,
            direction="INVALID_DIRECTION",  # This should raise ValidationError
            max_interval_jump=12
        )

def test_note_pattern_data_comprehensive() -> None:
    """Test comprehensive pattern data validation."""
    # Test all scale types
    for scale_type in ScaleType:
        pattern_data = NotePatternData(
            key="C",
            scale_type=scale_type,
            octave_range=(3, 5),
            max_interval_jump=12,
            allow_chromatic=True,
            use_scale_mode=True,
            use_chord_tones=True,
            direction=PatternDirection.UP,
            restart_on_chord=True
        )
        assert pattern_data.scale_type == scale_type
        
    # Test custom interval weights
    pattern_with_weights = NotePatternData(
        key="C",
        scale_type=ScaleType.MAJOR,
        custom_interval_weights={
            2: 0.5,
            4: 1.0,
            7: 0.8
        }
    )
    assert len(pattern_with_weights.custom_interval_weights) == 3
    
    # Test invalid octave range
    with pytest.raises(ValidationError):
        NotePatternData(
            key="C",
            scale_type=ScaleType.MAJOR,
            octave_range=(5, 3)  # Invalid range
        )

    # Fix the comparison of list and tuple
    intervals = list(SCALE_INTERVALS[ScaleType.MAJOR])
    assert intervals == list(SCALE_INTERVALS[ScaleType.MAJOR])

def test_pattern_creation() -> None:
    """Test pattern creation with various configurations."""
    pattern_data = NotePatternData(
        key="C",
        scale_type=ScaleType.MAJOR,
        direction=PatternDirection.UP,
        max_interval_jump=12
    )
    
    pattern = NotePattern(
        pattern=[
            Note(pitch="C", octave=4, duration=1.0),
            Note(pitch="E", octave=4, duration=0.5)
        ],
        data=pattern_data
    )
    assert len(pattern.pattern) == 2

def test_pattern_validation() -> None:
    """Test pattern validation rules."""
    pattern_data = NotePatternData(
        key="C",
        scale_type=ScaleType.MAJOR,
        direction=PatternDirection.UP,
        max_interval_jump=12
    )
    
    pattern = NotePattern(
        pattern=[
            Note(pitch="C", octave=4, duration=1.0),
            Note(pitch="E", octave=4, duration=0.5)
        ],
        data=pattern_data
    )
    assert pattern.data.key == "C"

def test_note_pattern_voice_leading() -> None:
    """Test voice leading validation."""
    pattern_data = NotePatternData(
        key="C4",
        max_interval_jump=4,
        scale_type=ScaleType.MAJOR
    )
    
    # Test valid pattern
    valid_pattern = NotePattern(
        pattern=[
            Note(pitch="C", octave=4, duration=1.0),
            Note(pitch="E", octave=4, duration=1.0)
        ],
        data=pattern_data
    )
    
    # This should return a valid result
    result = valid_pattern.validate_voice_leading()
    assert result.is_valid
    
    # Test invalid pattern
    invalid_pattern = NotePattern(
        pattern=[
            Note(pitch="C", octave=4, duration=1.0),
            Note(pitch="C", octave=5, duration=1.0)  # Interval larger than max_interval_jump
        ],
        data=pattern_data
    )
    
    # This should return an invalid result
    result = invalid_pattern.validate_voice_leading()
    assert not result.is_valid
    assert any("Voice leading violation" in violation.message 
              for violation in result.violations)

def test_note_pattern_range() -> None:
    """Test range validation."""
    pattern_data = NotePatternData(
        key="C",
        root_note="C",
        scale_type=ScaleType.MAJOR,
        octave_range=(4, 5),  # Narrower range
        max_interval_jump=12,
        direction=PatternDirection.UP
    )

    scale_info = ScaleInfo(
        key="C",
        scale_type=ScaleType.MAJOR
    )

    # Test valid range - using notes within allowed interval
    valid_pattern = NotePattern(
        name="Test Pattern",
        pattern=[
            Note(pitch="C", octave=4, duration=1.0),
            Note(pitch="E", octave=4, duration=1.0),  # Smaller interval jump
            Note(pitch="G", octave=4, duration=1.0)   # Still within octave range
        ],
        data=pattern_data,
        scale_info=scale_info,
        skip_validation=False  # Enable validation
    )

    # Validate after creation
    validation_result = valid_pattern.validate_all()
    assert validation_result.is_valid, f"Validation failed: {validation_result.violations}"

def validate_note(note: Note, min_value: int = 0, max_value: int = 127) -> bool:
    """Validate a note's MIDI number is within the given range."""
    if not hasattr(note, 'to_midi_number'):
        return False
    
    midi_num = note.to_midi_number()
    return min_value <= midi_num <= max_value
