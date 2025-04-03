import pytest
from note_gen.core.enums import (
    ScaleType,
    ChordQuality,
    PatternDirection,
    NoteModificationType,
    SequenceType,
    ErrorType
)

def test_scale_type_intervals():
    """Test that scale intervals are correctly defined for all scale types."""
    for scale_type in ScaleType:
        intervals = scale_type.intervals  # Changed from get_scale_intervals to intervals property
        assert isinstance(intervals, tuple)
        assert all(isinstance(i, int) for i in intervals)
        
        # For non-chromatic scales, verify intervals are within valid range
        if scale_type != ScaleType.CHROMATIC:
            assert all(0 <= i <= 11 for i in intervals)
            assert len(intervals) == 7  # All diatonic scales have 7 notes
        else:
            assert len(intervals) == 12  # Chromatic scale has 12 notes
            assert intervals == tuple(range(12))

def test_scale_type_values():
    """Test that all scale types have proper string values."""
    expected_types = {
        "MAJOR", "MINOR", "HARMONIC_MINOR", "MELODIC_MINOR",
        "DORIAN", "PHRYGIAN", "LYDIAN", "MIXOLYDIAN",
        "LOCRIAN", "CHROMATIC"
    }
    actual_types = {member.value for member in ScaleType}
    assert actual_types == expected_types

def test_chord_quality_values():
    """Test that all chord qualities are properly defined."""
    expected_qualities = {
        'MINOR', 'DOMINANT_ELEVENTH', 'MAJOR_ELEVENTH', 'MAJOR_SEVENTH',
        'SUSPENDED_FOURTH', 'AUGMENTED', 'DIMINISHED_SEVENTH',
        'HALF_DIMINISHED_SEVENTH', 'DIMINISHED', 'SUSPENDED_SECOND',
        'DOMINANT', 'MAJOR_NINTH', 'MINOR_NINTH', 'MINOR_ELEVENTH',
        'MINOR_SEVENTH', 'DOMINANT_SEVENTH', 'MAJOR'
    }
    actual_qualities = {q.name for q in ChordQuality}
    assert actual_qualities == expected_qualities

def test_pattern_direction_values():
    """Test pattern direction enum values."""
    assert PatternDirection.UP.value == "up"
    assert PatternDirection.DOWN.value == "down"
    assert PatternDirection.RANDOM.value == "random"
    assert PatternDirection.ALTERNATE.value == "alternate"

def test_note_modification_values():
    """Test note modification type enum values."""
    expected_mods = {
        "transpose", "invert", "retrograde",
        "augment", "diminish"
    }
    actual_mods = {member.value for member in NoteModificationType}
    assert actual_mods == expected_mods

def test_sequence_type_values():
    """Test sequence type enum values."""
    expected = {'LINEAR', 'CIRCULAR', 'RANDOM', 'RHYTHMIC'}  # Updated to uppercase
    actual = set(SequenceType.__members__.keys())
    assert actual == expected

def test_error_type_values():
    """Test error type enum values."""
    expected = {
        'VALIDATION_ERROR',
        'CHORD_ERROR',
        'SCALE_ERROR',
        'PATTERN_ERROR'
    }  # Updated to uppercase
    actual = set(ErrorType.__members__.keys())
    assert actual == expected

@pytest.mark.parametrize("scale_type,expected_length", [
    (ScaleType.MAJOR, 7),
    (ScaleType.MINOR, 7),
    (ScaleType.HARMONIC_MINOR, 7),
    (ScaleType.MELODIC_MINOR, 7),
    (ScaleType.CHROMATIC, 12),
])
def test_scale_interval_lengths(scale_type, expected_length):
    """Test that each scale type has the correct number of intervals."""
    intervals = scale_type.intervals  # Changed from get_scale_intervals to intervals property
    assert len(intervals) == expected_length
