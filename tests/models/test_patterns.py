import pytest
from src.note_gen.models.rhythm_pattern import RhythmPatternData, RhythmNote


def test_rhythm_pattern_data() -> None:
    notes = [RhythmNote(1, 1, 1), RhythmNote(0, 0, 1), RhythmNote(1, 1, 1)]
    rhythm_pattern_data = RhythmPatternData(notes)
    assert rhythm_pattern_data == RhythmPatternData(notes)  # Replace with actual test logic
