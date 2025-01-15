"""Tests for the RhythmPattern model."""

import pytest
from note_gen.models.rhythm_pattern import RhythmPattern, RhythmNote, RhythmPatternData

def test_rhythm_note_validation():
    """Test RhythmNote validation."""
    # Test valid note
    note = RhythmNote(duration=1.0, is_rest=False, velocity=80)
    assert note.duration == 1.0
    assert note.is_rest is False
    assert note.velocity == 80

    # Test invalid duration
    with pytest.raises(ValueError):
        RhythmNote(duration=-1.0)

    # Test invalid velocity
    with pytest.raises(ValueError):
        RhythmNote(duration=1.0, velocity=150)

def test_rhythm_pattern_validation():
    """Test RhythmPattern validation."""
    # Test valid pattern
    data = RhythmPatternData(
        notes=[
            RhythmNote(position=0.0, duration=1.0, velocity=100),
            RhythmNote(position=1.0, duration=0.5, velocity=80, is_rest=True)
        ],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        groove_type="straight",
        variation_probability=0.0,
        duration=1.5,
        style="basic"
    )
    
    pattern = RhythmPattern(
        name="Test Pattern",
        data=data
    )
    
    assert pattern.name == "Test Pattern"
    assert len(pattern.data.notes) == 2
    assert pattern.data.total_duration == 1.5  # position(1.0) + duration(0.5)
    assert sum(1 for note in pattern.data.notes if note.is_rest) == 1
    assert sum(1 for note in pattern.data.notes if not note.is_rest) == 1

    # Test pattern with invalid note
    with pytest.raises(ValueError):
        invalid_data = RhythmPatternData(
            notes=[RhythmNote(duration=-1.0)],
            time_signature="4/4"
        )
        RhythmPattern(
            name="Invalid Pattern",
            data=invalid_data
        )

def test_rhythm_pattern_dict_conversion():
    """Test RhythmPattern to/from dictionary conversion."""
    data = RhythmPatternData(
        notes=[
            RhythmNote(position=0.0, duration=1.0, velocity=100),
            RhythmNote(position=1.0, duration=0.5, velocity=80, is_rest=True)
        ],
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        groove_type="straight",
        variation_probability=0.0,
        duration=1.5,
        style="basic"
    )
    
    pattern = RhythmPattern(
        name="Test Pattern",
        data=data,
        description="A test pattern",
        tags=["test", "rhythm"],
        complexity=1.2
    )

    pattern_dict = pattern.model_dump()
    assert pattern_dict["name"] == "Test Pattern"
    assert len(pattern_dict["data"]["notes"]) == 2
    assert pattern_dict["description"] == "A test pattern"
    assert pattern_dict["tags"] == ["test", "rhythm"]
    assert pattern_dict["complexity"] == 1.2

    # Convert back to RhythmPattern
    new_pattern = RhythmPattern(**pattern_dict)
    assert new_pattern.name == pattern.name
    assert len(new_pattern.data.notes) == len(pattern.data.notes)
    assert new_pattern.description == pattern.description
    assert new_pattern.tags == pattern.tags
    assert new_pattern.complexity == pattern.complexity
