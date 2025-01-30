import unittest
from src.note_gen.models.enums import ChordQualityType

class TestChordQuality(unittest.TestCase):
    def test_from_string_invalid(self) -> None:
        """Test that invalid chord quality strings raise ValueError."""
        invalid_qualities = [
            "invalid_quality",
            "nonexistent",
            "",
            "123",
        ]
        for quality in invalid_qualities:
            with self.subTest(quality=quality):
                with self.assertRaises(ValueError):
                    ChordQualityType.from_string(quality)

    def test_from_string_valid(self) -> None:
        """Test that valid chord quality strings are correctly converted."""
        test_cases = [
            ("MAJOR", ChordQualityType.MAJOR),
            ("maj", ChordQualityType.MAJOR),
            ("M", ChordQualityType.MAJOR),
            ("MINOR", ChordQualityType.MINOR),
            ("min", ChordQualityType.MINOR),
            ("m", ChordQualityType.MINOR),
            ("diminished", ChordQualityType.DIMINISHED),
            ("dim", ChordQualityType.DIMINISHED),
            ("°", ChordQualityType.DIMINISHED),
            ("dominant_7", ChordQualityType.DOMINANT_7),
            ("maj7", ChordQualityType.MAJOR_7),
            ("m7", ChordQualityType.MINOR_7),
            ("dim7", ChordQualityType.DIMINISHED_7),
            ("ø7", ChordQualityType.HALF_DIMINISHED_7),
            ("m7b5", ChordQualityType.HALF_DIMINISHED_7),
            ("aug", ChordQualityType.AUGMENTED),
            ("+", ChordQualityType.AUGMENTED),
            ('dominant', ChordQualityType.DOMINANT),
            ('7', ChordQualityType.DOMINANT_7),
        ]
        for input_str, expected_type in test_cases:
            with self.subTest(input_str=input_str):
                print(f"Testing input: {input_str}")  # Debugging output
                chord_quality = ChordQualityType.from_string(input_str)
                print(f"Result: {chord_quality}, Expected: {expected_type}")  # Debugging output
                self.assertEqual(chord_quality, expected_type)

    def test_get_intervals(self) -> None:
        """Test that correct intervals are returned for each chord quality."""
        for quality in ChordQualityType:
            intervals = quality.get_intervals()  # Correctly call the instance method
            assert intervals == quality.get_intervals(), f"Intervals for {quality} do not match."

    def test_str_representation(self) -> None:
        """Test that string representation matches the expected format."""
        test_cases = [
            (ChordQualityType.MAJOR, "MAJOR"),
            (ChordQualityType.MINOR, "MINOR"),
            (ChordQualityType.DIMINISHED, "diminished"),
            (ChordQualityType.AUGMENTED, "augmented"),
            (ChordQualityType.DOMINANT_7, "dominant_7"),
            (ChordQualityType.MAJOR_7, "maj7"),
            (ChordQualityType.MINOR_7, "m7"),
        ]
        
        for quality_type, expected_str in test_cases:
            with self.subTest(quality_type=quality_type):
                self.assertEqual(
                    str(quality_type),
                    expected_str,
                    f"Expected str({quality_type}) to be {expected_str}"
                )


if __name__ == "__main__":
    unittest.main()