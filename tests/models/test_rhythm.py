"""Test rhythm pattern functionality."""
from src.note_gen.models.rhythm import RhythmPattern , RhythmNote
from src.note_gen.core.enums import ScaleType

def test_basic_rhythm_pattern():
    """Test basic rhythm pattern creation and validation."""
    pattern = RhythmPattern(
        name="Basic Pattern",
        pattern=[
            RhythmNote(position=0.0, duration=1.0, velocity=64),
            RhythmNote(position=1.0, duration=1.0, velocity=64),
            RhythmNote(position=2.0, duration=1.0, velocity=64),
            RhythmNote(position=3.0, duration=1.0, velocity=64)
        ],
        time_signature=(4, 4),
        description="Test Pattern"
    )
    
    assert pattern.name == "Basic Pattern"
    assert len(pattern.pattern) == 4
    assert pattern.time_signature == (4, 4)
    assert pattern.description == "Test Pattern"
