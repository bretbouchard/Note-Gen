import pytest
from note_gen.models.pattern_type import PatternType


def test_pattern_ascending() -> None:
    notes = ['C', 'D', 'E']
    expected = ['C', 'D', 'E']
    assert PatternType.ASCENDING.get_pattern(notes) == expected


def test_pattern_descending() -> None:
    notes = ['C', 'D', 'E']
    expected = ['E', 'D', 'C']
    assert PatternType.DESCENDING.get_pattern(notes) == expected


def test_pattern_ascending_descending() -> None:
    notes = ['C', 'D', 'E']
    expected = ['C', 'D', 'E', 'D', 'C']
    assert PatternType.ASCENDING_DESCENDING.get_pattern(notes) == expected


def test_pattern_descending_ascending() -> None:
    notes = ['C', 'D', 'E']
    expected = ['E', 'D', 'C', 'D', 'E']
    assert PatternType.DESCENDING_ASCENDING.get_pattern(notes) == expected


def test_pattern_random() -> None:
    notes = ['C', 'D', 'E']
    result = PatternType.RANDOM.get_pattern(notes)
    assert len(result) == len(notes)  # Ensure length is the same
    assert set(result) == set(notes)  # Ensure all notes are present


def test_pattern_invalid() -> None:
    with pytest.raises(ValueError):
        PatternType('invalid').get_pattern(['C'])
