"""Tests for note pattern models."""
import pytest
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.note import Note
from note_gen.models.scale_info import ScaleInfo
from note_gen.core.enums import ScaleType, PatternDirection

@pytest.fixture
def basic_pattern() -> NotePattern:
    """Create a basic valid note pattern for testing."""
    return NotePattern(
        name="Basic Pattern",
        pattern=[
            Note(pitch="C", octave=4, duration=1.0, velocity=100, position=0.0, stored_midi_number=60),
            Note(pitch="E", octave=4, duration=1.0, velocity=100, position=1.0, stored_midi_number=64),
            Note(pitch="G", octave=4, duration=1.0, velocity=100, position=2.0, stored_midi_number=67)
        ],
        data=NotePatternData(
            key="C",
            scale_type=ScaleType.MAJOR,
            allow_parallel_motion=True  # Set to True for basic pattern
        ),
        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    )

def test_scale_compatibility():
    """Test scale compatibility validation."""
    pattern = NotePattern(
        name="Test Pattern",
        pattern=[
            Note(pitch="C", octave=4, duration=1.0, velocity=100, position=0.0, stored_midi_number=60),
            Note(pitch="C#", octave=4, duration=1.0, velocity=100, position=1.0, stored_midi_number=61)  # Not in C major scale
        ],
        data=NotePatternData(
            key="C",
            scale_type=ScaleType.MAJOR,
            allow_chromatic=False
        ),
        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    )

    with pytest.raises(ValueError) as exc_info:
        pattern.enable_validation()  # Use the new method instead

    assert "SCALE_COMPATIBILITY_ERROR" in str(exc_info.value)

def test_parallel_motion():
    """Test detection of parallel motion."""
    pattern = NotePattern(
        name="Test Pattern",
        pattern=[
            Note(pitch="C", octave=4, duration=1.0, velocity=100, position=0.0, stored_midi_number=60),
            Note(pitch="D", octave=4, duration=1.0, velocity=100, position=1.0, stored_midi_number=62),
            Note(pitch="E", octave=4, duration=1.0, velocity=100, position=2.0, stored_midi_number=64)
        ],
        data=NotePatternData(
            key="C",
            scale_type=ScaleType.MAJOR,
            allow_parallel_motion=False,
            allow_chromatic=True
        ),
        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    )

    with pytest.raises(ValueError) as exc_info:
        pattern.enable_validation()  # Use the new method instead

    assert "PARALLEL_MOTION_ERROR" in str(exc_info.value)

def test_consonance():
    """Test consonance validation."""
    pattern = NotePattern(
        name="Dissonance Test",
        pattern=[
            Note(pitch="C", octave=4, duration=1.0, velocity=100, position=0.0, stored_midi_number=60),
            Note(pitch="C#", octave=4, duration=1.0, velocity=100, position=1.0, stored_midi_number=61)
        ],
        data=NotePatternData(
            key="C",
            scale_type=ScaleType.MAJOR,
            allow_chromatic=True,
            allow_parallel_motion=True
        ),
        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    )

    with pytest.raises(ValueError) as exc_info:
        pattern.enable_validation()  # Use the new method instead

    assert "CONSONANCE_ERROR" in str(exc_info.value)

def test_valid_pattern(basic_pattern: NotePattern) -> None:
    # Should not raise any exceptions
    basic_pattern.validate_musical_rules()

def test_pattern_data_validation() -> None:
    data = {
        "name": "Test Pattern",
        "pattern": [
            {"pitch": "C", "octave": 4, "duration": 1.0},
            {"pitch": "E", "octave": 4, "duration": 1.0},
            {"pitch": "G", "octave": 4, "duration": 1.0}
        ],
        "data": {
            "scale_type": ScaleType.MAJOR,
            "key": "C",
            "max_interval_jump": 12
        },
        "scale_info": {
            "key": "C",
            "scale_type": ScaleType.MAJOR
        }
    }

    result = NotePattern.validate_pattern_data(data)
    assert result.is_valid, f"Validation failed: {result.violations}"

def test_invalid_pattern_data() -> None:
    data = {
        "name": "Invalid Pattern",
    }

    with pytest.raises(ValueError, match="Pattern cannot be empty"):
        NotePattern(**data)
