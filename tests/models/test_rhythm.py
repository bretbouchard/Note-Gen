import pytest
from src.note_gen.models.patterns import RhythmPattern


def test_rhythm_pattern_creation():
    pattern = RhythmPattern(pattern=['4n', '8n', '8n', '4n'])
    assert len(pattern.pattern) == 4
    assert all(isinstance(item, dict) for item in pattern.pattern)


def test_rhythm_pattern_string_representation():
    pattern = RhythmPattern(pattern=['4n', '8n', '8n', '4n'])
    assert str(pattern) == "{'value': '4n'} {'value': '8n'} {'value': '8n'} {'value': '4n'}"


def test_rhythm_pattern_validation():
    with pytest.raises(ValueError):
        RhythmPattern(pattern=['invalid'])
