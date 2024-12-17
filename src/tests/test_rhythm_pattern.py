import pytest
from models.rhythm_pattern import RhythmPattern


def test_rhythm_pattern_creation():
    pattern = RhythmPattern(name="Quarter Notes", data=[1, 1, 1, 1])
    assert pattern.name == "Quarter Notes"
    assert pattern.data == [1, 1, 1, 1]


def test_rhythm_pattern_apply_groove():
    pattern = RhythmPattern(name="Groove Pattern", data=[1, 1, 1, 1])
    pattern.apply_groove()
    assert pattern.data != [1, 1, 1, 1]  # Assuming groove changes the pattern
