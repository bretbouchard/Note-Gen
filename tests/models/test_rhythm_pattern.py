import unittest
from pydantic import ValidationError
from src.note_gen.models.patterns import RhythmPattern, ChordPatternItem, ChordProgressionPattern

class TestRhythmPattern(unittest.TestCase):
    def test_validate_pattern_required(self):
        """Test that pattern is required."""
        with self.assertRaises(ValidationError):
            RhythmPattern(name="Test Pattern")

    def test_validate_pattern_format(self):
        """Test pattern format validation."""
        with self.assertRaises(ValidationError):
            RhythmPattern(name="Test Pattern", pattern=[1, 2, 3])  # Should be string

    def test_validate_pattern_type_safety(self):
        """Test pattern type safety."""
        with self.assertRaises(ValidationError):
            RhythmPattern(name="Test Pattern", pattern=123)  # Should be string

    def test_validate_duration_mismatch_pattern(self):
        """Test duration validation against time signature."""
        with self.assertRaises(ValidationError):
            RhythmPattern(
                name="Test Pattern",
                pattern="1 1 1",  # Only 3 beats in 4/4
                time_signature="4/4"
            )
