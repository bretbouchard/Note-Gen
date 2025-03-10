import unittest
import pytest
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note import Note
import logging
from pydantic import BaseModel
from typing import Dict, Any
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)

class ChordInput(BaseModel):
    root: Dict[str, Any]  # This will represent the root note
    quality: str  # This can be the string representation of the chord quality

class TestChordQuality(unittest.TestCase):

    def test_get_intervals(self) -> None:
        """Test that correct intervals are returned for each chord quality."""
        # Get all valid chord qualities
        test_cases = [
            (ChordQuality.MAJOR, [0, 4, 7]),
            (ChordQuality.MINOR, [0, 3, 7]),
            (ChordQuality.DIMINISHED, [0, 3, 6]),
            (ChordQuality.AUGMENTED, [0, 4, 8]),
            (ChordQuality.DOMINANT, [0, 4, 7]),
            (ChordQuality.MAJOR9, [0, 4, 7, 11, 14]),
            (ChordQuality.MINOR9, [0, 3, 7, 10, 14]),
            (ChordQuality.DOMINANT9, [0, 4, 7, 10, 14]),
            (ChordQuality.MAJOR11, [0, 4, 7, 11, 14, 17]),
            (ChordQuality.MINOR11, [0, 3, 7, 10, 14, 17]),
            (ChordQuality.DOMINANT11, [0, 4, 7, 10, 14, 17]),
            (ChordQuality.SUS2, [0, 2, 7]),
            (ChordQuality.SUS4, [0, 5, 7]),
            (ChordQuality.SEVEN_SUS4, [0, 5, 7, 10]),
            (ChordQuality.FLAT5, [0, 4, 6]),
            (ChordQuality.FLAT7, [0, 4, 7, 9]),
            (ChordQuality.SHARP5, [0, 4, 8]),
            (ChordQuality.SHARP7, [0, 4, 7, 11]),
            (ChordQuality.SUSPENDED, [0, 5, 7]),
        ]
        for quality, expected_intervals in test_cases:
            intervals = quality.get_intervals()  
            logger.debug(f"Quality: {quality}, Expected: {expected_intervals}, Actual: {intervals}")
            self.assertEqual(intervals, expected_intervals)

    def test_from_string_valid(self) -> None:
        """Test that valid chord quality strings are correctly converted."""
        test_cases = [
            ("MAJOR", ChordQuality.MAJOR),
            ("maj", ChordQuality.MAJOR),
            ("M", ChordQuality.MAJOR),
            ("MINOR", ChordQuality.MINOR),
            ("min", ChordQuality.MINOR),
            ("m", ChordQuality.MINOR),
            ("DIMINISHED", ChordQuality.DIMINISHED),
            ("Diminished", ChordQuality.DIMINISHED),
            ("diminished", ChordQuality.DIMINISHED),
            ("dim", ChordQuality.DIMINISHED),
            ("°", ChordQuality.DIMINISHED),
            ("dominant", ChordQuality.DOMINANT),
            ("dominant7", ChordQuality.DOMINANT_SEVENTH),
            ("maj7", ChordQuality.MAJOR_SEVENTH),
            ("m7", ChordQuality.MINOR_SEVENTH),
            ("dim7", ChordQuality.FULL_DIMINISHED),
            ("ø7", ChordQuality.HALF_DIMINISHED),
            ("m7b5", ChordQuality.HALF_DIMINISHED),
            ("aug", ChordQuality.AUGMENTED),
            ("+", ChordQuality.AUGMENTED),
            ("7", ChordQuality.DOMINANT_SEVENTH),
            ("MAJOR7", ChordQuality.MAJOR_SEVENTH),
            ("MINOR7", ChordQuality.MINOR_SEVENTH),
            ("DIMINISHED7", ChordQuality.FULL_DIMINISHED),
        ]
        for input_str, expected_type in test_cases:
            with self.subTest(input_str=input_str):
                chord_quality = ChordQuality.from_string(input_str)  
                self.assertEqual(chord_quality, expected_type)

    def test_invalid_quality_string(self) -> None:
        """Test that invalid quality strings raise ValueError."""
        with self.assertRaises(ValueError):
            ChordQuality.from_string('invalid_quality')  

    def test_get_intervals_invalid_quality(self) -> None:
        """Test that get_intervals raises a ValueError for invalid chord qualities."""
        # Create a fake chord quality that's not in the enum
        # This will use mock to create a MagicMock object with name attribute set to 'INVALIDQUALITY'
        with self.assertRaises(ValueError):
            invalid_quality = MagicMock()
            invalid_quality.__str__.return_value = "INVALIDQUALITY"
            # Make sure it's not in the intervals dictionary
            ChordQuality.MAJOR.get_intervals.__self__.__class__.get_intervals(invalid_quality)

    def test_get_intervals_undefined_quality(self) -> None:
        """Test that get_intervals raises a ValueError for undefined chord qualities."""
        with self.assertRaises(ValueError):
            ChordQuality.from_string('UNDEFINED')  

    def test_chord_quality_variations(self) -> None:
        root_note = Note.from_name("C4", duration=1.0, velocity=64)

        # Create a dictionary for the root note
        root_dict = {
            "note_name": root_note.note_name,
            "octave": root_note.octave,
            "duration": root_note.duration,
            "velocity": root_note.velocity,
        }

        # Test various quality strings
        for quality_str in ['maj7', 'MAJOR7', 'major7']:
            logger.debug(f"Testing chord quality: {quality_str}")  # Logging
            chord_quality = ChordQuality.from_string(quality_str)  # Convert string to ChordQuality
            chord = Chord(root=root_dict, quality=chord_quality)  # Pass the enum value
            logger.debug(f"Chord quality after initialization: {chord.quality}")  # Logging the quality
            assert chord.quality == ChordQuality.MAJOR_SEVENTH, f"Failed for quality: {quality_str}"

        invalid_quality_strings = ['invalid_quality']  

        for quality_str in invalid_quality_strings:
            logger.debug(f"Testing invalid chord quality: {quality_str}")  # Logging
            with pytest.raises(ValueError, match="Invalid chord quality"):  # Updated to match actual error message
                chord_input = ChordInput(root=root_dict, quality=quality_str)  # This will raise an error if invalid
                chord = Chord(**chord_input.dict())  # This line won't be reached if the input is invalid

        logger.debug(f"Testing invalid chord quality: invalid_quality")  # Logging
        with pytest.raises(ValueError, match="Invalid chord quality"):  # Updated to match actual error message
            chord_quality = ChordQuality.from_string('invalid_quality')
            
        # Empty string defaults to MAJOR
        logger.debug(f"Testing empty chord quality string")  # Logging
        chord_quality = ChordQuality.from_string('')
        assert chord_quality == ChordQuality.MAJOR, "Empty string should default to MAJOR"

    def test_invalid_quality(self) -> None:
        """Test that invalid chord quality raises ValueError."""
        root_note = Note.from_name("C4", duration=1.0, velocity=64)
        with self.assertRaises(ValueError):
            Chord(root=root_note, quality='INVALID_QUALITY')

    def test_str_representation(self) -> None:
        """Test that string representation matches the expected format."""
        test_cases = [
            (ChordQuality.MAJOR, "MAJOR"),
            (ChordQuality.MINOR, "MINOR"),
            (ChordQuality.DIMINISHED, "DIMINISHED"),
            (ChordQuality.AUGMENTED, "AUGMENTED"),
            (ChordQuality.DOMINANT, "DOMINANT"),
            (ChordQuality.MAJOR9, "MAJOR9"),
            (ChordQuality.MINOR9, "MINOR9"),
        ]
        for quality_type, expected_str in test_cases:
            with self.subTest(quality_type=quality_type):
                result_str = str(quality_type)
                logger.debug(f"Testing str representation: {result_str} against expected: {expected_str}")
                self.assertEqual(result_str, expected_str)

if __name__ == "__main__":
    unittest.main()