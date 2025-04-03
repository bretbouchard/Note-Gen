import unittest
from unittest.mock import MagicMock
from pydantic import ValidationError
from note_gen.models.chord import Chord
from note_gen.models.note import Note
from note_gen.core.enums import ChordQuality

class TestChordQuality(unittest.TestCase):
    def test_chord_quality_variations(self) -> None:
        """Test different chord qualities."""
        chord = Chord(root="C", quality=ChordQuality.MAJOR)
        self.assertEqual(chord.quality, ChordQuality.MAJOR)
        
        chord = Chord(root="C", quality=ChordQuality.MINOR)
        self.assertEqual(chord.quality, ChordQuality.MINOR)

    def test_from_string_valid(self) -> None:
        """Test valid string to ChordQuality conversion."""
        self.assertEqual(ChordQuality.from_string("maj"), ChordQuality.MAJOR)
        self.assertEqual(ChordQuality.from_string("m"), ChordQuality.MINOR)

    def test_get_intervals(self) -> None:
        """Test getting intervals for different chord qualities."""
        major_intervals = ChordQuality.get_intervals(ChordQuality.MAJOR)
        self.assertEqual(major_intervals, [0, 4, 7])
        
        minor_intervals = ChordQuality.get_intervals(ChordQuality.MINOR)
        self.assertEqual(minor_intervals, [0, 3, 7])
        
        dim_intervals = ChordQuality.get_intervals(ChordQuality.DIMINISHED)
        self.assertEqual(dim_intervals, [0, 3, 6])

    def test_get_intervals_invalid_quality(self) -> None:
        """Test that get_intervals raises ValueError for invalid chord qualities."""
        # Create a mock enum that's not a valid ChordQuality
        mock_quality = MagicMock(spec=ChordQuality)
        mock_quality.__str__ = MagicMock(return_value="INVALIDQUALITY")
        
        with self.assertRaises(ValueError) as context:
            ChordQuality.get_intervals(mock_quality)
        self.assertIn("Invalid chord quality", str(context.exception))

    def test_invalid_quality(self) -> None:
        """Test that invalid chord quality raises ValidationError when creating a Chord."""
        with self.assertRaises(ValidationError) as context:
            Chord(root="C", quality="INVALID_QUALITY")
        self.assertIn("Input should be", str(context.exception))

    def test_invalid_quality_string(self) -> None:
        """Test that invalid quality string raises ValueError."""
        with self.assertRaises(ValueError):
            ChordQuality.from_string("invalid")

    def test_str_representation(self) -> None:
        """Test string representation of chord qualities."""
        self.assertEqual(str(ChordQuality.MAJOR), "MAJOR")
        self.assertEqual(str(ChordQuality.MINOR), "MINOR")

if __name__ == "__main__":
    unittest.main()
