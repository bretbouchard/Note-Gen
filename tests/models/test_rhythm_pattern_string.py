"""Tests for rhythm pattern string representation."""
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote

def test_rhythm_pattern_string_representation() -> None:
    # Create a pattern with notes and rests
    pattern = RhythmPattern(
        name="Test Pattern",
        time_signature=(4, 4),  # Changed to tuple format
        pattern=[
            RhythmNote(**{
                "position": 0.0,
                "duration": 1.0,
                "velocity": 64,
                "accent": False,
                "tuplet_ratio": (1, 1),
                "groove_offset": 0.0
            }),
            RhythmNote(**{
                "position": 1.0,
                "duration": 0.5,
                "velocity": 51,
                "accent": False,
                "tuplet_ratio": (1, 1),
                "groove_offset": 0.0
            }),
            RhythmNote(**{
                "position": 1.5,
                "duration": 0.5,
                "velocity": 58,
                "accent": False,
                "tuplet_ratio": (1, 1),
                "groove_offset": 0.0
            })
        ]
    )

    # Test string representation
    expected_str = "Test Pattern (4/4)"
    assert str(pattern) == expected_str

    # Test pattern validation
    assert len(pattern.pattern) == 3
    assert pattern.pattern[0].duration == 1.0
    assert pattern.pattern[1].duration == 0.5
    assert pattern.pattern[2].duration == 0.5
