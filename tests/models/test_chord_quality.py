import unittest
from src.note_gen.models.chord_quality import ChordQuality
from src.note_gen.models.enums import ChordQualityType

class TestChordQuality(unittest.TestCase):
    def test_from_string_valid(self) -> None:
        # Check a few known mappings
        self.assertEqual(ChordQuality.from_string("major").quality, ChordQualityType.MAJOR)
        self.assertEqual(ChordQuality.from_string("minor").quality, ChordQualityType.MINOR)
        self.assertEqual(ChordQuality.from_string("diminished").quality, ChordQualityType.DIMINISHED)
        self.assertEqual(ChordQuality.from_string("dominant").quality, ChordQualityType.DOMINANT)
        self.assertEqual(ChordQuality.from_string("maj7").quality, ChordQualityType.MAJOR_SEVENTH)
        self.assertEqual(ChordQuality.from_string("sus2").quality, ChordQualityType.SUS2)

    def test_from_string_invalid(self) -> None:
        with self.assertRaises(ValueError):
            ChordQuality.from_string("not_a_quality")

    def test_from_string_none(self) -> None:
        with self.assertRaises(ValueError):
            ChordQuality.from_string(None)  # type: ignore

if __name__ == "__main__":
    unittest.main()