import unittest
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestChordQuality(unittest.TestCase):

    def test_get_intervals(self) -> None:
        """Test that correct intervals are returned for each chord quality."""
        # Get all valid chord qualities
        chord_qualities = list(ChordQualityType)
        expected_intervals = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.DOMINANT7: [0, 4, 7, 10],
            ChordQualityType.MAJOR7: [0, 4, 7, 11],
            ChordQualityType.MINOR7: [0, 3, 7, 10],
            ChordQualityType.DIMINISHED7: [0, 3, 6, 9],
            ChordQualityType.HALF_DIMINISHED7: [0, 3, 6, 10],
            ChordQualityType.DOMINANT: [0, 4, 7, 10],
            ChordQualityType.MAJOR9: [0, 4, 7, 11],
            ChordQualityType.MINOR9: [0, 3, 7, 10, 14],
            ChordQualityType.DOMINANT9: [0, 4, 7, 10, 14],
            ChordQualityType.AUGMENTED7: [0, 4, 8, 10],
            ChordQualityType.MAJOR11: [0, 4, 7, 11, 14],
            ChordQualityType.MINOR11: [0, 3, 7, 10, 14],
            ChordQualityType.DOMINANT11: [0, 4, 7, 10, 14, 17],
            ChordQualityType.SUS2: [0, 2, 7],
            ChordQualityType.SUS4: [0, 5, 7],
            ChordQualityType.SEVEN_SUS4: [0, 5, 7, 10],
            ChordQualityType.FLAT5: [0, 4, 6],
            ChordQualityType.FLAT7: [0, 4, 7, 9],
            ChordQualityType.SHARP5: [0, 4, 8],
            ChordQualityType.SHARP7: [0, 4, 7, 11],
        }
        for quality in chord_qualities:
            intervals = ChordQualityType.get_intervals(quality)
            self.assertEqual(intervals, expected_intervals[quality])

    def test_from_string_valid(self) -> None:
        """Test that valid chord quality strings are correctly converted."""
        test_cases = [
            ("MAJOR", ChordQualityType.MAJOR),
            ("maj", ChordQualityType.MAJOR),
            ("M", ChordQualityType.MAJOR),
            ("MINOR", ChordQualityType.MINOR),
            ("min", ChordQualityType.MINOR),
            ("m", ChordQualityType.MINOR),
            ("DIMINISHED", ChordQualityType.DIMINISHED),
            ("Diminished", ChordQualityType.DIMINISHED),
            ("diminished", ChordQualityType.DIMINISHED),
            ("dim", ChordQualityType.DIMINISHED),
            ("°", ChordQualityType.DIMINISHED),
            ("dominant7", ChordQualityType.DOMINANT7),
            ("maj7", ChordQualityType.MAJOR7),
            ("m7", ChordQualityType.MINOR7),
            ("dim7", ChordQualityType.DIMINISHED7),
            ("ø7", ChordQualityType.HALF_DIMINISHED7),
            ("m7b5", ChordQualityType.HALF_DIMINISHED7),
            ("aug", ChordQualityType.AUGMENTED),
            ("+", ChordQualityType.AUGMENTED),
            ("dominant", ChordQualityType.DOMINANT),
            ("7", ChordQualityType.DOMINANT7),
        ]
        for input_str, expected_type in test_cases:
            with self.subTest(input_str=input_str):
                print(f"Testing input: {input_str}")
                logger.debug(f"ChordQualityType: {ChordQualityType}")
                logger.debug(f"ChordQualityType is recognized: {ChordQualityType is not None}")
                chord_quality = ChordQualityType.from_string(input_str)
                print(f"Result: {chord_quality}, Expected: {expected_type}")
                self.assertEqual(chord_quality, expected_type)

    def test_invalid_quality_string(self):
        """Test that invalid quality strings raise ValueError."""
        with self.assertRaises(ValueError):
            ChordQualityType.from_string('invalid_quality')

    def test_get_intervals_invalid_quality(self) -> None:
        """Test that get_intervals raises a ValueError for invalid chord qualities."""
        with self.assertRaises(ValueError):
            # Create a string that's not a valid enum value
            ChordQualityType.get_intervals('INVALID' + 'QUALITY')

    def test_get_intervals_undefined_quality(self) -> None:
        """Test that get_intervals raises a ValueError for undefined chord qualities."""
        with self.assertRaises(ValueError):
            ChordQualityType.from_string('UNDEFINED')

    def test_chord_quality_variations(self):
        """Test that invalid chord quality variations raise ValueError."""
        test_cases = [
            ('C', 'invalid_quality'),
            ('C', 'invalid_quality2'),
            ('C', 'invalid_quality3'),
        ]
        for root, quality in test_cases:
            with self.subTest(root=root, quality=quality):
                with self.assertRaises(ValueError):
                    Chord(root='C', quality=quality)

    def test_invalid_quality(self) -> None:
        """Test that invalid chord quality raises ValueError."""
        root_note = Note.from_name("C4", duration=1.0, velocity=64)
        with self.assertRaises(ValueError):
            Chord(root=root_note, quality='INVALID_QUALITY')

    def test_str_representation(self) -> None:
        """Test that string representation matches the expected format."""
        test_cases = [
            (ChordQualityType.MAJOR, "MAJOR"),
            (ChordQualityType.MINOR, "MINOR"),
            (ChordQualityType.DIMINISHED, "DIMINISHED"),
            (ChordQualityType.AUGMENTED, "AUGMENTED"),
            (ChordQualityType.DOMINANT7, "DOMINANT7"),
            (ChordQualityType.MAJOR7, "MAJOR7"),
            (ChordQualityType.MINOR7, "MINOR7"),
        ]
        
        for quality_type, expected_str in test_cases:
            with self.subTest(quality_type=quality_type):
                result_str = str(quality_type)
                logger.debug(f"Testing str representation: {result_str} against expected: {expected_str}")
                self.assertEqual(result_str, expected_str)

if __name__ == "__main__":
    unittest.main()