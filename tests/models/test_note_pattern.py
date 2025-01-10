import unittest
import pytest
from pydantic import ValidationError
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.note import Note

# Unittest-based tests
class TestNotePattern(unittest.TestCase):
    def test_create_note_pattern(self) -> None:
        # Create a basic NotePattern instance with some notes and intervals
        pattern = NotePattern(
            name="TestPattern",
            data=[0, 4],
            notes=[Note(note_name='C', octave=4), Note(note_name='E', octave=4)],
            description="",
            tags=[],
        )
        # Verify basic properties
        self.assertEqual(pattern.name, "TestPattern")
        self.assertEqual(pattern.data, [0, 4])
        self.assertEqual(pattern.notes, [Note(note_name='C', octave=4), Note(note_name='E', octave=4)])
        # Check that optional fields default as expected if not provided
        self.assertEqual(pattern.description, "")
        self.assertEqual(pattern.tags, [])

    def test_getters_return_expected_types(self) -> None:
        # Construct a minimal pattern data and pattern
        pattern = NotePattern(
            name="Pattern1",
            data=[0, 2],
            notes=[Note(note_name='C', octave=4), Note(note_name='D', octave=4)],
            description="",
            tags=[],
        )
        
        # Call the getter methods and check types; specifics depend on implementation.
        notes = pattern.get_notes()
        intervals = pattern.data
        duration = pattern.total_duration

        self.assertIsInstance(notes, list)
        self.assertTrue(all(isinstance(n, Note) for n in notes))
        self.assertIsInstance(intervals, list)
        self.assertTrue(all(isinstance(i, int) or isinstance(i, list) for i in intervals))
        self.assertIsInstance(duration, float)

# Pytest-style tests
def test_create_note_pattern() -> None:
    pattern = NotePattern(name="Test Pattern", data=[1, 2, 3], notes=[])
    assert pattern.name == "Test Pattern"
    assert pattern.data == [1, 2, 3]

def test_invalid_data() -> None:
    """Test that creating a NotePattern with invalid data raises an error."""
    with pytest.raises(ValidationError):
        NotePattern(name="Invalid Pattern", data=None, notes=[])

def test_note_pattern_empty_data() -> None:
    """Test that creating a NotePattern with empty data is handled."""
    with pytest.raises(ValueError, match="Data must be a non-empty list of integers or nested lists"):
        NotePattern(name="Empty Pattern", data=[], notes=[])

def test_note_pattern_complex_data() -> None:
    """Test a NotePattern with valid complex data."""
    pattern = NotePattern(name="Complex Pattern", data=[1, 2, 3, 4], notes=[])
    assert pattern.data == [1, 2, 3, 4]

def test_note_pattern_valid_nested_data() -> None:
    """Test a NotePattern with valid nested data."""
    pattern = NotePattern(name="Valid Pattern", data=[1, [2, 3], 4], notes=[])
    assert pattern.data == [1, [2, 3], 4]

def test_note_pattern_invalid_data() -> None:
    """Test a NotePattern with invalid data."""
    with pytest.raises(ValueError, match="Data must be a non-empty list of integers or nested lists"):
        NotePattern(name="Invalid Pattern", data=[1, "string", 4], notes=[])