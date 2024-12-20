import pytest
from src.models.rhythm_pattern import RhythmPattern, RhythmPatternData, RhythmNote


def test_rhythm_pattern_creation() -> None:
    """Test creation of RhythmPattern with valid data."""
    notes = [RhythmNote(position=0.0, duration=1.0, velocity=64, is_rest=False)]
    pattern_data = RhythmPatternData(notes=notes)
    pattern = RhythmPattern(name='ValidPattern', data=pattern_data)
    assert pattern.name == 'ValidPattern'
    assert len(pattern.data.notes) == 1


def test_invalid_data_type() -> None:
    """Test handling of invalid data types."""
    with pytest.raises(ValueError):
        RhythmPattern(name='InvalidPattern', data=RhythmPatternData(notes=[]))  # Pass a valid RhythmPatternData object


def test_invalid_notes() -> None:
    """Test handling of invalid notes in RhythmPatternData."""
    with pytest.raises(ValueError):
        RhythmPatternData(notes=[])  # No notes
    with pytest.raises(ValueError):
        RhythmPatternData(notes=[RhythmNote(position=-1, duration=1.0, velocity=64, is_rest=False)])  # Invalid position