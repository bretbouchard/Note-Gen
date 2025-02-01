import unittest
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Chord, Note
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestChordQuality(unittest.TestCase):

    def test_get_intervals(self) -> None:
        """Test that correct intervals are returned for each chord quality."""
        # Filter to only include actual chord qualities
        chord_qualities = [quality for quality in ChordQualityType if quality != ChordQualityType.CHORD_QUALITY_ALIASES]
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
            ChordQualityType.MINOR9: [0, 3, 7, 10, 14],  # Updated expected intervals for MINOR9
            ChordQualityType.DOMINANT9: [0, 4, 7, 10, 14],  # Expected intervals for DOMINANT9
            ChordQualityType.AUGMENTED7: [0, 4, 8, 10],  # Expected intervals for AUGMENTED7
            ChordQualityType.MAJOR11: [0, 4, 7, 11, 14],  # Expected intervals for MAJOR11
            ChordQualityType.MINOR11: [0, 3, 7, 10, 14],  # Expected intervals for MINOR11
            ChordQualityType.DOMINANT11: [0, 4, 7, 10, 14, 17],  # Expected intervals for DOMINANT11
            ChordQualityType.SUS2: [0, 2, 7],  # Expected intervals for SUS2
            ChordQualityType.SUS4: [0, 5, 7],  # Expected intervals for SUS4
            ChordQualityType.SEVEN_SUS4: [0, 5, 7, 10],  # Expected intervals for SEVEN_SUS4
            ChordQualityType.FLAT5: [0, 4, 6],  # Expected intervals for FLAT5
            ChordQualityType.FLAT7: [0, 4, 7, 9],  # Expected intervals for FLAT7
            ChordQualityType.SHARP5: [0, 4, 8],  # Expected intervals for SHARP5
            ChordQualityType.SHARP7: [0, 4, 7, 11],  # Expected intervals for SHARP5
        }
        for quality in chord_qualities:
            if quality == ChordQualityType.INVALID:
                with self.assertRaises(ValueError) as context:
                    ChordQualityType.get_intervals(quality)  # Correctly call the method
                self.assertEqual(str(context.exception), "No intervals defined for chord quality: INVALID.")
            elif quality == ChordQualityType.INVALID_QUALITY:
                with self.assertRaises(ValueError) as context:
                    ChordQualityType.get_intervals(quality)  # Correctly call the method
                self.assertEqual(str(context.exception), "No intervals defined for chord quality: INVALID_QUALITY.")
            else:
                intervals = ChordQualityType.get_intervals(quality)  # Correctly call the method
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
            ("DIMINISHED", ChordQualityType.DIMINISHED),  # Uppercase version
            ("Diminished", ChordQualityType.DIMINISHED),  # Mixed case
            ("diminished", ChordQualityType.DIMINISHED),
            ("dim", ChordQualityType.DIMINISHED),
            ("°", ChordQualityType.DIMINISHED),
            ("dominant7", ChordQualityType.DOMINANT7),  # Removed underscore
            ("maj7", ChordQualityType.MAJOR7),
            ("m7", ChordQualityType.MINOR7),
            ("dim7", ChordQualityType.DIMINISHED7),
            ("ø7", ChordQualityType.HALF_DIMINISHED7),
            ("m7b5", ChordQualityType.HALF_DIMINISHED7),
            ("aug", ChordQualityType.AUGMENTED),
            ("+", ChordQualityType.AUGMENTED),
            ("dominant", ChordQualityType.DOMINANT),
            ("7", ChordQualityType.DOMINANT7),  # Changed to match enum
        ]
        for input_str, expected_type in test_cases:
            with self.subTest(input_str=input_str):
                print(f"Testing input: {input_str}")  # Debugging output
                logger.debug(f"ChordQualityType: {ChordQualityType}")  # Log the enum to check recognition
                logger.debug(f"ChordQualityType is recognized: {ChordQualityType is not None}")  # Log the enum to check recognition
                chord_quality = ChordQualityType.from_string(input_str)
                print(f"Result: {chord_quality}, Expected: {expected_type}")  # Debugging output
                self.assertEqual(chord_quality, expected_type)

    def test_invalid_quality_string(self):
        root_note = 'C'
        with self.assertRaises(ValueError):
            Chord(root=root_note, quality='invalid_quality')

    def test_get_intervals_invalid_quality(self) -> None:
        """Test that get_intervals raises a ValueError for invalid chord qualities."""
        quality_instance = ChordQualityType.INVALID
        with self.assertRaises(ValueError):
            ChordQualityType.get_intervals(quality_instance)  # Correctly call the method

    def test_get_intervals_undefined_quality(self) -> None:
        """Test that get_intervals raises a ValueError for undefined chord qualities."""
        with self.assertRaises(ValueError):
            undefined_quality = ChordQualityType('UNDEFINED')  # Assuming UNDEFINED is not a valid quality
            _ = undefined_quality.get_intervals()

    def test_chord_quality_variations(self):
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
        root_note = Note.from_name("C4", duration=1.0, velocity=64)
        with self.assertRaises(ValueError):
            Chord(root=root_note, quality=ChordQualityType.INVALID_QUALITY)

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
                self.assertEqual(
                    result_str,
                    expected_str,
                    f"Expected str({quality_type}) to be {expected_str}"
                )


if __name__ == "__main__":
    unittest.main()