import pytest
from pydantic import ValidationError , validator
from src.note_gen.models.note_pattern import NotePattern


def test_create_note_pattern() -> None:
    pattern = NotePattern(name="Test Pattern", data=[1, 2, 3])
    assert pattern.name == "Test Pattern"
    assert pattern.data == [1, 2, 3]

def test_invalid_data() -> None:
    """Test that creating a NotePattern with invalid data raises an error."""
    with pytest.raises(ValidationError):
        NotePattern(name="Invalid Pattern", data=None)

def test_note_pattern_empty_data() -> None:
    """Test that creating a NotePattern with empty data is handled."""
    with pytest.raises(ValueError, match="Data must be a non-empty list of integers or nested lists"):
        NotePattern(name="Empty Pattern", data=[])

def test_note_pattern_complex_data() -> None:
    """Test a NotePattern with valid complex data."""
    pattern = NotePattern(name="Complex Pattern", data=[1, 2, 3, 4])
    assert pattern.data == [1, 2, 3, 4]

def test_note_pattern_valid_nested_data() -> None:
    """Test a NotePattern with valid nested data."""
    pattern = NotePattern(name="Valid Pattern", data=[1, [2, 3], 4])
    assert pattern.data == [1, [2, 3], 4]

def test_note_pattern_invalid_data() -> None:
    """Test a NotePattern with invalid data."""
    with pytest.raises(ValueError, match="Data must be a non-empty list of integers or nested lists"):
        NotePattern(name="Invalid Pattern", data=[1, "string", 4])