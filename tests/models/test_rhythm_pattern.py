"""Tests for rhythm pattern models."""
import pytest
from note_gen.models.rhythm import RhythmPattern, RhythmNote

@pytest.fixture
def basic_rhythm_pattern() -> RhythmPattern:
    """Create a basic rhythm pattern for testing."""
    return RhythmPattern(
        name="test_pattern",
        time_signature=(4, 4),
        pattern=[
            RhythmNote(position=0.0, duration=1.0, velocity=64, accent=True),
            RhythmNote(position=1.0, duration=1.0, velocity=64, accent=False),
            RhythmNote(position=2.0, duration=1.0, velocity=64, accent=True),
            RhythmNote(position=3.0, duration=1.0, velocity=64, accent=False)
        ]
    )

def test_rhythm_pattern_creation(basic_rhythm_pattern: RhythmPattern) -> None:
    """Test basic rhythm pattern creation."""
    assert basic_rhythm_pattern.name == "test_pattern"
    assert basic_rhythm_pattern.time_signature == (4, 4)
    assert len(basic_rhythm_pattern.pattern) == 4
    assert basic_rhythm_pattern.total_duration == 4.0

def test_invalid_rhythm_pattern():
    """Test invalid rhythm pattern creation."""
    with pytest.raises(ValueError):
        RhythmPattern(
            name="Invalid Pattern",
            pattern=[
                RhythmNote(position=1.0, duration=1.0),  # Out of order
                RhythmNote(position=0.0, duration=1.0)
            ],
            time_signature=(4, 4)
        )

def test_rhythm_pattern_validation():
    """Test rhythm pattern validation."""
    # Test invalid time signature
    with pytest.raises(ValueError):
        RhythmPattern(
            name="test",
            time_signature=(3, 3),  # Invalid denominator
            pattern=[RhythmNote(position=0.0, duration=1.0)]
        )

    # Test unordered positions
    with pytest.raises(ValueError):
        RhythmPattern(
            name="test",
            time_signature=(4, 4),
            pattern=[
                RhythmNote(position=1.0, duration=1.0),
                RhythmNote(position=0.0, duration=1.0)
            ]
        )

def test_rhythm_note_properties() -> None:
    """Test RhythmNote properties and methods."""
    note = RhythmNote(
        position=1.0,
        duration=1.0,
        velocity=64,
        accent=True,
        tuplet_ratio=(2, 3)  # Triplet
    )
    
    assert note.get_actual_duration() == pytest.approx(0.666666, rel=1e-5)
    assert note.accent is True
    assert note.velocity == 64

def test_rhythm_pattern_swing() -> None:
    """Test rhythm pattern with swing enabled."""
    pattern = RhythmPattern(
        name="swing_pattern",
        swing_enabled=True,
        time_signature=(4, 4),
        pattern=[
            RhythmNote(
                position=0.0,
                duration=0.5,
                velocity=64,
                swing_ratio=0.67
            ),
            RhythmNote(
                position=0.5,
                duration=0.5,
                velocity=64,
                swing_ratio=0.33
            )
        ]
    )
    assert pattern.swing_enabled
    assert len(pattern.pattern) == 2
    assert pattern.pattern[0].swing_ratio == 0.67
    assert pattern.pattern[1].swing_ratio == 0.33
