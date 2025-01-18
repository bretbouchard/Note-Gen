import unittest

from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.scale import Scale, ScaleType
from src.note_gen.models.roman_numeral import RomanNumeral
from unittest.mock import patch


class FakeScale(Scale):
    def __init__(self, root: Note, scale_type: ScaleType):
        super().__init__(root=root, scale_type=scale_type)

    def get_degree_of_note(self, note: Note) -> int:
        note_to_degree = {"C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "A": 6, "B": 7}
        if note.note_name == "X":
            raise TypeError("Simulating an unexpected error.")
        if note.note_name not in note_to_degree:
            raise ValueError(f"Note {note.note_name} not in scale.")
        return note_to_degree[note.note_name]


class TestRomanNumeral(unittest.TestCase):
    def test_get_roman_numeral_from_chord_major(self) -> None:
        scale = FakeScale(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)
        chord = Chord(root=Note(note_name="C", octave=4, duration=1, velocity=100), quality=ChordQualityType.MAJOR)  # Use a valid quality
        result = RomanNumeral.get_roman_numeral_from_chord(chord, scale)
        self.assertEqual(result, "I")

    def test_from_scale_degree_minor(self) -> None:
        for degree in range(1, 8):
            with self.subTest(degree=degree):
                numeral = RomanNumeral.from_scale_degree(degree, ChordQualityType.MINOR)
                expected = RomanNumeral.INT_TO_ROMAN[degree].lower()
                self.assertEqual(numeral, expected)

    def test_from_scale_degree_diminished(self) -> None:
        degree = 3
        numeral = RomanNumeral.from_scale_degree(degree, ChordQualityType.DIMINISHED)
        self.assertEqual(numeral, "iiio")

    def test_from_scale_degree_augmented(self) -> None:
        degree = 4
        numeral = RomanNumeral.from_scale_degree(degree, ChordQualityType.AUGMENTED)
        self.assertEqual(numeral, "IV+")

    def test_from_scale_degree_minor_7(self) -> None:
        degree = 2
        numeral = RomanNumeral.from_scale_degree(degree, ChordQualityType.MINOR_7)
        self.assertEqual(numeral, "ii7")

    def test_from_scale_degree_major_7(self) -> None:
        degree = 1
        numeral = RomanNumeral.from_scale_degree(degree, ChordQualityType.MAJOR_7)
        self.assertEqual(numeral, "IΔ")

    def test_from_scale_degree_dominant_7(self) -> None:
        degree = 5
        numeral = RomanNumeral.from_scale_degree(degree, ChordQualityType.DOMINANT)
        self.assertEqual(numeral, "V7")

    def test_from_scale_degree_invalid_degree(self) -> None:
        with self.assertRaises(ValueError):
            RomanNumeral.from_scale_degree(0, ChordQualityType.MAJOR)
        with self.assertRaises(ValueError):
            RomanNumeral.from_scale_degree(8, ChordQualityType.MAJOR)
        with self.assertRaises(ValueError):
            RomanNumeral.from_scale_degree(1, "InvalidQuality")

    def test_to_scale_degree_valid(self) -> None:
        test_data = [
            ("I", 1),
            ("i", 1),
            ("ii", 2),
            ("III", 3),
            ("v", 5),
            ("VII", 7),
        ]
        for numeral, expected in test_data:
            with self.subTest(numeral=numeral):
                result = RomanNumeral.to_scale_degree(numeral)
                self.assertEqual(result, expected)

    def test_to_scale_degree_invalid(self) -> None:
        for invalid_numeral in ["", "IX", "iix", "random"]:
            with self.subTest(numeral=invalid_numeral):
                with self.assertRaises(ValueError):
                    RomanNumeral.to_scale_degree(invalid_numeral)

    def test_roman_numeral_creation(self) -> None:
        numeral = RomanNumeral(
            scale_degree=1,
            quality=ChordQualityType.MAJOR
        )
        self.assertEqual(numeral.scale_degree, 1)
        self.assertEqual(numeral.quality, ChordQualityType.MAJOR)
        with self.assertRaises(ValueError):
            RomanNumeral(scale_degree=0, quality=ChordQualityType.MAJOR)
        with self.assertRaises(ValueError):
            RomanNumeral(scale_degree=1, quality="InvalidQuality")

    def test_get_roman_numeral_from_chord_different_degrees(self) -> None:
        scale = FakeScale(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)
        test_data = [
            (Chord(root=Note(note_name="D", octave=4, duration=1, velocity=100), quality=ChordQualityType.MINOR), "ii"),
            (Chord(root=Note(note_name="E", octave=4, duration=1, velocity=100), quality=ChordQualityType.DIMINISHED), "iiio"),
            (Chord(root=Note(note_name="A", octave=4, duration=1, velocity=100), quality=ChordQualityType.MINOR_7), "vi7"),
            (Chord(root=Note(note_name="G", octave=4, duration=1, velocity=100), quality=ChordQualityType.DOMINANT), "V7"),
        ]
        for chord, expected_numeral in test_data:
            with self.subTest(chord=chord):
                result = RomanNumeral.get_roman_numeral_from_chord(chord, scale)
                self.assertEqual(result, expected_numeral)

    def test_get_roman_numeral_from_chord_note_not_in_scale(self) -> None:
        scale = FakeScale(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)
        chord = Chord(root=Note(note_name="C#"), quality=ChordQualityType.MAJOR)
        with self.assertRaises(ValueError) as cm:
            RomanNumeral.get_roman_numeral_from_chord(chord, scale)
        self.assertIn("not in scale", str(cm.exception))

    def test_get_roman_numeral_from_chord_unexpected_error(self) -> None:
        scale = FakeScale(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)
        chord = Chord(root=Note(note_name="C", octave=4, duration=1, velocity=100), quality=ChordQualityType.MAJOR)

        with patch.object(scale, 'get_degree_of_note', side_effect=TypeError("Simulating an unexpected error.")):
            with self.assertRaises(ValueError) as cm:
                RomanNumeral.get_roman_numeral_from_chord(chord, scale)
            self.assertIn("An unexpected error occurred", str(cm.exception))


if __name__ == "__main__":
    unittest.main()