import unittest
import pytest
from pydantic import ValidationError
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.models.note import Note

# Unittest-based tests
class TestNotePattern(unittest.TestCase):
    def test_create_note_pattern(self) -> None:
        pattern = NotePattern(
            name="TestPattern",
            pattern=[0, 2, 4],
            description="Test pattern description",
            tags=['valid_tag'],
            complexity=0.5
        )
        # Verify basic properties
        self.assertEqual(pattern.name, "TestPattern")
        self.assertEqual(pattern.pattern, [0, 2, 4])
        self.assertEqual(pattern.tags, ['valid_tag'])

    def test_name_validation(self) -> None:
        """Test name validation rules."""
        # Test valid names
        NotePattern(
            name="Valid Pattern",
            pattern=[0, 2, 4],
            description="Valid pattern description",
            tags=['valid_tag'],
            complexity=0.5
        )

        # Test invalid names
        with pytest.raises(ValidationError, match="String should have at least 2 characters"):
            NotePattern(
                name="A",
                pattern=[0, 2, 4],
                description="Invalid pattern description",
                tags=['valid_tag'],
                complexity=0.5
            )


    def test_pattern_validation(self) -> None:
        """Test pattern validation rules."""
        # Test valid pattern
        NotePattern(
            name="Valid Pattern",
            pattern=[0, 2, 4],
            description="Valid pattern description",
            tags=['valid_tag'],
            complexity=0.5
        )

        # Test invalid patterns
        with pytest.raises(ValidationError, match="Pattern must not be empty"):
            NotePattern(
                name="Empty Pattern",
                pattern=[],
                description="A pattern with no data",
                tags=['valid_tag'],
                complexity=0.5
            )

        with pytest.raises(ValidationError, match="Interval 13 is outside reasonable range"):
            NotePattern(
                name="Invalid Pattern",
                pattern=[0, 13, 4],
                description="Invalid pattern description",
                tags=['valid_tag'],
                complexity=0.5
            )

    def test_complexity_validation(self) -> None:
        """Test complexity validation rules."""
        # Test valid complexity
        NotePattern(
            name="Valid Pattern",
            pattern=[0, 2, 4],
            description="Valid pattern description",
            tags=['valid_tag'],
            complexity=0.5
        )

        # Test invalid complexity
        with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
            NotePattern(
                name="Invalid Pattern",
                pattern=[0, 2, 4],
                description="Invalid pattern description",
                tags=['valid_tag'],
                complexity=1.5
            )

    def test_tags_validation(self) -> None:
        """Test tags validation rules."""
        # Test valid tags
        NotePattern(
            name="Valid Pattern",
            pattern=[0, 2, 4],
            description="Valid pattern description",
            tags=['valid_tag', 'another_tag'],
            complexity=0.5
        )

        # Test invalid tags
        with pytest.raises(ValidationError, match="Tags must contain non-whitespace strings"):
            NotePattern(
                name="Invalid Pattern",
                pattern=[0, 2, 4],
                description="Invalid pattern description",
                tags=['', '   '],
                complexity=0.5
            )

    def test_add_remove_tag(self) -> None:
        """Test add_tag and remove_tag methods."""
        pattern = NotePattern(
            name="Test Pattern",
            pattern=[0, 2, 4],
            description="Test pattern description",
            tags=['initial_tag'],
            complexity=0.5
        )

        pattern.add_tag('new_tag')
        assert 'new_tag' in pattern.tags

        pattern.remove_tag('initial_tag')
        assert 'initial_tag' not in pattern.tags

def test_invalid_data() -> None:
    """Test that creating a NotePattern with invalid data raises an error."""
    with pytest.raises(ValidationError):
        NotePattern(
            name="Invalid Pattern",
            pattern=[],  # Empty pattern should raise validation error
            description="Test invalid pattern",
            tags=["test"],
            complexity=1.5  # Invalid complexity
        )

def test_note_pattern_empty_data() -> None:
    """Test that creating a NotePattern with empty data is handled."""
    with pytest.raises(ValueError, match="Pattern must not be empty"):
        NotePattern(
            name="Empty Pattern",
            pattern=[],
            description="A pattern with no data",
            tags=['valid_tag'],
            complexity=0.5
        )

def test_note_pattern_complex_data() -> None:
    """Test a NotePattern with valid complex data."""
    pattern = NotePattern(
        name="Complex Pattern",
        pattern=[0, 2, 4],
        description="Complex pattern description",
        tags=['valid_tag'],
        complexity=0.5
    )
    assert pattern.pattern == [0, 2, 4]

def test_note_pattern_valid_nested_data() -> None:
    """Test a NotePattern with valid complex data."""
    pattern = NotePattern(
        name="Valid Pattern",
        pattern=[0, 2, 4],
        description="Valid pattern description",
        tags=['valid_tag'],
        complexity=0.5
    )
    assert pattern.pattern == [0, 2, 4]

def test_note_pattern_invalid_data() -> None:
    """Test a NotePattern with invalid data.
    
    The pattern should contain only integers, so we're testing with a non-integer value
    that should properly fail validation, rather than restricting the range of valid 
    interval values, which could limit legitimate musical patterns with large intervals.
    """
    with pytest.raises(ValidationError):
        NotePattern(
            name="Invalid Pattern",
            pattern=[0, "X", 4],  # Using a non-integer value instead of a large interval
            description="Invalid pattern description",
            tags=['valid_tag'],
            complexity=0.5
        )