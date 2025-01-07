import unittest
from unittest.mock import patch
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale import ScaleType
from pydantic import ValidationError
import random

class FakeScaleInfo(ScaleInfo):
    def get_scale_degree_note(self, degree: int) -> Note:
        note_map = {
            1: Note(note_name="C"),
            2: Note(note_name="D"),
            3: Note(note_name="E"),
            4: Note(note_name="F"),
            5: Note(note_name="G"),
            6: Note(note_name="A"),
            7: Note(note_name="B"),
        }
        return note_map.get(degree, Note(note_name="C"))  # Default to C if degree not found

    def get_chord_quality_for_degree(self, degree: int) -> str:
        # Pretend it returns "major" or "minor" depending on parity
        return "major" if degree % 2 == 1 else "minor"

    def get_scale_notes(self) -> list[Note]:
        return [Note(note_name="C"), Note(note_name="D"), Note(note_name="E")]

class TestChordProgressionGenerator(unittest.TestCase):
    def test_no_pattern_provided_raises_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate(pattern=None)

    def test_invalid_pattern_raises_validation_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, pattern=["nonexistent"])
        with self.assertRaises(ValueError):  # Update expectation to ValueError
            gen.generate()

    def test_generate_with_valid_pattern(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        # Use a known pattern from PROGRESSION_PATTERNS: "I-IV-V"
        gen = ChordProgressionGenerator(scale_info=scale_info, pattern=["I-IV-V"])
        progression = gen.generate()
        self.assertEqual(len(progression.chords), 3)
        self.assertIsInstance(progression.chords[0], Chord)

    def test_generate_custom_with_mismatched_lists_raises_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate_custom(degrees=[1, 2], qualities=["major"])

    def test_generate_custom_valid(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info)
        progression = gen.generate_custom(degrees=[1, 2], qualities=["major", "minor"])
        self.assertEqual(len(progression.chords), 2)
        self.assertEqual(progression.chords[0].quality, ChordQualityType.MAJOR)
        self.assertEqual(progression.chords[1].quality, ChordQualityType.MINOR)

    def test_generate_random_valid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info)
        # Patch random.choice to control output
        with patch.object(random, 'choice', side_effect=[1, "major", 3, "minor"]):
            progression = gen.generate_random(length=2)
        self.assertEqual(len(progression.chords), 2)
        self.assertEqual(progression.chords[0].root.note_name, "C")
        self.assertEqual(progression.chords[1].root.note_name, "E")

    def test_generate_random_invalid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate_random(length=-1)

    def test_generate_chord_valid(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info)
        chord = gen.generate_chord("i")  # maps to scale_degree=1 (see RomanNumeral code)
        # In FakeScaleInfo, 1 -> "C"
        self.assertEqual(chord.root.note_name, "C")
        self.assertEqual(chord.quality, ChordQualityType.MAJOR)  # Because get_chord_quality_for_degree(1) -> 'major'

    def test_generate_chord_invalid_numeral(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate_chord("random-numeral")

if __name__ == "__main__":
    unittest.main()