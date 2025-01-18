import unittest
from src.note_gen.models.chord_quality import ChordQuality
from src.note_gen.models.enums import ChordQualityType

class TestChordQuality(unittest.TestCase):
    def test_from_string_valid(self) -> None:
        """Test that valid chord quality strings are correctly converted."""
        test_cases = [
            ("major", ChordQualityType.MAJOR),
            ("maj", ChordQualityType.MAJOR),
            ("M", ChordQualityType.MAJOR),
            ("minor", ChordQualityType.MINOR),
            ("min", ChordQualityType.MINOR),
            ("m", ChordQualityType.MINOR),
            ("diminished", ChordQualityType.DIMINISHED),
            ("dim", ChordQualityType.DIMINISHED),
            ("°", ChordQualityType.DIMINISHED),
            ("7", ChordQualityType.DOMINANT_7),
            ("maj7", ChordQualityType.MAJOR_7),
            ("m7", ChordQualityType.MINOR_7),
            ("dim7", ChordQualityType.DIMINISHED_7),
            ("ø7", ChordQualityType.HALF_DIMINISHED_7),
            ("m7b5", ChordQualityType.HALF_DIMINISHED_7),
            ("aug", ChordQualityType.AUGMENTED),
            ("+", ChordQualityType.AUGMENTED),
        ]
        
        for input_str, expected_type in test_cases:
            with self.subTest(input_str=input_str):
                chord_quality = ChordQuality.from_string(input_str)
                self.assertEqual(
                    chord_quality.quality_type, 
                    expected_type,
                    f"Expected {input_str} to convert to {expected_type}, got {chord_quality.quality_type}"
                )

    def test_from_string_invalid(self) -> None:
        """Test that invalid chord quality strings raise ValueError."""
        invalid_qualities = [
            "not_a_quality",
            "",
            "invalid",
            "123",
            None,  # type: ignore
        ]
        
        for invalid_str in invalid_qualities:
            with self.subTest(invalid_str=invalid_str):
                with self.assertRaises(ValueError):
                    ChordQuality.from_string(invalid_str)

    def test_get_intervals(self) -> None:
        """Test that correct intervals are returned for each chord quality."""
        test_cases = [
            (ChordQualityType.MAJOR, [0, 4, 7]),
            (ChordQualityType.MINOR, [0, 3, 7]),
            (ChordQualityType.DIMINISHED, [0, 3, 6]),
            (ChordQualityType.AUGMENTED, [0, 4, 8]),
            (ChordQualityType.DOMINANT_7, [0, 4, 7, 10]),
            (ChordQualityType.MAJOR_7, [0, 4, 7, 11]),
            (ChordQualityType.MINOR_7, [0, 3, 7, 10]),
            (ChordQualityType.DIMINISHED_7, [0, 3, 6, 9]),
            (ChordQualityType.HALF_DIMINISHED_7, [0, 3, 6, 10]),
        ]
        
        for quality_type, expected_intervals in test_cases:
            with self.subTest(quality_type=quality_type):
                chord_quality = ChordQuality(quality_type=quality_type)
                self.assertEqual(
                    chord_quality.get_intervals(),
                    expected_intervals,
                    f"Expected {quality_type} to have intervals {expected_intervals}"
                )

    def test_str_representation(self) -> None:
        """Test that string representation matches the expected format."""
        test_cases = [
            (ChordQualityType.MAJOR, "major"),
            (ChordQualityType.MINOR, "minor"),
            (ChordQualityType.DIMINISHED, "diminished"),
            (ChordQualityType.AUGMENTED, "augmented"),
            (ChordQualityType.DOMINANT_7, "7"),
            (ChordQualityType.MAJOR_7, "maj7"),
            (ChordQualityType.MINOR_7, "m7"),
        ]
        
        for quality_type, expected_str in test_cases:
            with self.subTest(quality_type=quality_type):
                chord_quality = ChordQuality(quality_type=quality_type)
                self.assertEqual(
                    str(chord_quality),
                    expected_str,
                    f"Expected str({quality_type}) to be {expected_str}"
                )

if __name__ == "__main__":
    unittest.main()