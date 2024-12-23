import pytest
from src.note_gen.models.rhythm_pattern import RhythmPatternData, RhythmNote


def test_rhythm_pattern_data() -> None:
    notes = [
        RhythmNote(position=1, duration=1, velocity=1),
        RhythmNote(position=0, duration=1, velocity=1),  # Ensure duration is positive
        RhythmNote(position=1, duration=1, velocity=1)
    ]
    rhythm_pattern_data = RhythmPatternData(notes=notes)  # Use keyword argument
    assert rhythm_pattern_data == RhythmPatternData(notes=notes)  # Replace with actual test logic
