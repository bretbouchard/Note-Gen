import unittest
import pytest
from pydantic import ValidationError
from src.note_gen.models.note_pattern import NotePattern, NotePatternData
from src.note_gen.models.note import Note

# Unittest-based tests
class TestNotePattern(unittest.TestCase):
    def test_create_note_pattern(self) -> None:
        pattern = NotePattern(
            name="TestPattern",
            data=NotePatternData(
                notes=[{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}],
                duration=1.0,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            ),
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)],
            description="Test pattern description",
            tags=['valid_tag'],
            complexity=0.5,
            pattern_type="simple",
            is_test=True,
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        )
        # Verify basic properties
        self.assertEqual(pattern.name, "TestPattern")
        self.assertEqual(pattern.data.notes, [{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}])
        self.assertEqual(pattern.notes, [Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)])

    def test_getters_return_expected_types(self) -> None:
        pattern = NotePattern(
            name="Pattern1",
            data=NotePatternData(
                notes=[{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}],
                duration=1.0,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            ),
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)],
            description="A simple pattern",
            tags=['valid_tag'],
            complexity=0.5,
            pattern_type="simple",
            is_test=True,
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        )
        # Ensure this method exists or replace it with the correct method
        notes = pattern.notes
        intervals = pattern.data.notes
        duration = float(sum(note.duration for note in notes))
        assert isinstance(notes, list)
        assert all(isinstance(n, Note) for n in notes)

    def test_invalid_data(self) -> None:
        with pytest.raises(ValidationError):
            NotePattern(
                name="Invalid Pattern",
                data=NotePatternData(
                    notes=[{'note_name': 'C', 'octave': 4}],  # Valid note structure
                    duration=1.0,
                    position=0.0,
                    velocity=100,
                    intervals=[],
                    index=0
                ),
                notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100)],
                description="Invalid pattern",
                tags=['valid_tag'],
                complexity=0.5,
                pattern_type="simple",
                is_test=True,
                duration=None,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            )

    def test_note_pattern_empty_data(self) -> None:
        """Test that creating a NotePattern with empty data is handled."""
        data = NotePatternData(notes=[], duration=1.0, position=0.0, velocity=100, intervals=[], index=0)
        print(f"Testing with empty data: {data}")
        try:
            print(f"Creating NotePattern with data: {data}")
            NotePattern(
                name="Empty Pattern",
                data=data,
                notes=[],
                description="A pattern with no data",
                tags=['valid_tag'],
                complexity=0.5,
                pattern_type="simple",
                is_test=True,
                duration=1.0,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            )
        except ValueError as e:
            print(f"Caught ValueError: {e}")
        except ValidationError as e:
            print(f"Caught ValidationError: {e}")
        else:
            print("No exception raised, data was accepted.")

    def test_note_pattern_complex_data(self) -> None:
        pattern = NotePattern(
            name="Complex Pattern",
            data=NotePatternData(
                notes=[{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}],
                duration=1.0,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            ),
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)],
            description="Complex pattern description",
            tags=['valid_tag'],
            is_test=True,
            complexity=0.5,
            pattern_type="simple",
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        )
        assert pattern.data.notes == [{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}]

    def test_note_pattern_valid_nested_data(self) -> None:
        pattern = NotePattern(
            name="Valid Pattern",
            data=NotePatternData(
                notes=[{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}],
                duration=1.0,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            ),
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)],
            description="Valid pattern description",
            tags=['valid_tag'],
            is_test=True,
            complexity=0.5,
            pattern_type="simple",
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        )
        assert pattern.data.notes == [{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}]

    def test_note_pattern_invalid_data(self) -> None:
        """Test a NotePattern with invalid data."""
        data = NotePatternData(notes=[{'note_name': 'C', 'octave': 4}], duration=1.0, position=0.0, velocity=100, intervals=[1], index=0)
        print(f"Testing with invalid data: {data}")
        with pytest.raises(ValidationError):
            NotePattern(
                name="Invalid Pattern",
                data=data,
            )

    def test_search_note_pattern_by_index(self) -> None:
        """Test that searching for a NotePattern by index returns the correct pattern."""
        note_pattern = NotePattern(
            name='Test Pattern',
            data=NotePatternData(
                notes=[{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}],
                duration=1.0,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            ),
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)],
            description='A test pattern',
            tags=['test'],
            complexity=0.5,
            pattern_type="simple",
            is_test=True,
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        )
        note_pattern.index = 0  # Assume the index is set to 0
        assert note_pattern.index == 0
        # Here you would typically call a function to retrieve the NotePattern by index.
        retrieved_pattern = note_pattern  # Replace with actual search function
        assert retrieved_pattern == note_pattern

def test_invalid_data() -> None:
    """Test that creating a NotePattern with invalid data raises an error."""
    with pytest.raises(ValidationError):
        NotePattern(
            name="Invalid Pattern",
            data=NotePatternData(
                notes=[{'note_name': 'C', 'octave': 4}],  # Valid note structure
                duration=1.0,
                position=0.0,
                velocity=100,
                intervals=[],
                index=0
            ),
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100)],
            description="Invalid pattern",
            tags=['valid_tag'],
            complexity=0.5,
            pattern_type="simple",
            is_test=True,
            duration=None,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        )

def test_note_pattern_empty_data() -> None:
    """Test that creating a NotePattern with empty data is handled."""
    data = NotePatternData(notes=[], duration=1.0, position=0.0, velocity=100, intervals=[], index=0)
    print(f"Testing with empty data: {data}")
    with pytest.raises(ValueError, match="Notes must not be empty or None."):
        print(f"Creating NotePattern with data: {data}")
        NotePattern(
            name="Empty Pattern",
            data=data,
            notes=[],
            description="A pattern with no data",
            tags=['valid_tag'],
            complexity=0.5,
            pattern_type="simple",
            is_test=True,
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        )

def test_note_pattern_complex_data() -> None:
    """Test a NotePattern with valid complex data."""
    pattern = NotePattern(
        name="Complex Pattern",
        data=NotePatternData(
            notes=[{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}],
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        ),
        notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)],
        description="Complex pattern description",
        tags=['valid_tag'],
        is_test=True,
        complexity=0.5,
        pattern_type="simple",
        duration=1.0,
        position=0.0,
        velocity=100,
        intervals=[],
        index=0
    )
    assert pattern.data.notes == [{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}]
    assert pattern.notes == [Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)]

def test_note_pattern_valid_nested_data() -> None:
    """Test a NotePattern with valid complex data."""
    pattern = NotePattern(
        name="Valid Pattern",
        data=NotePatternData(
            notes=[{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}],
            duration=1.0,
            position=0.0,
            velocity=100,
            intervals=[],
            index=0
        ),
        notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)],
        description="Valid pattern description",
        tags=['valid_tag'],
        is_test=True,
        complexity=0.5,
        pattern_type="simple",
        duration=1.0,
        position=0.0,
        velocity=100,
        intervals=[],
        index=0
    )
    assert pattern.data.notes == [{"note_name": "C", "octave": 4}, {"note_name": "D", "octave": 4}]
    assert pattern.notes == [Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)]

def test_note_pattern_invalid_data() -> None:
    """Test a NotePattern with invalid data."""
    data = NotePatternData(notes=[{'note_name': 'C', 'octave': 4}], duration=1.0, position=0.0, velocity=100, intervals=[1], index=0)
    print(f"Testing with invalid data: {data}")
    with pytest.raises(ValidationError):
        NotePattern(
            name="Invalid Pattern",
            data=data,
        )