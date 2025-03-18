import unittest


from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale, ScaleType
from src.note_gen.models.roman_numeral import RomanNumeral
from unittest.mock import patch


class FakeScale(Scale):
    def __init__(self, root: Note, scale_type: ScaleType):
        super().__init__(root=root, scale_type=scale_type)

    def get_degree_of_note(self, note: Note) -> int:
        note_to_degree = {"C": 1, "D": 2, "E": 3, "F": 4, "G": 5, "A": 6, "B": 7}
        if note.note_name not in note_to_degree:
            raise ValueError(f"Note {note.note_name} not in scale.")
        return note_to_degree[note.note_name]

    def get_notes(self):
        return [Note(note_name=name, octave=4, duration=1, velocity=100) for name in ["C", "D", "E", "F", "G", "A", "B"]]


class TestRomanNumeral(unittest.TestCase):
    def setUp(self):
        self.scale = FakeScale(
            root=Note(note_name="C", octave=4, duration=1, velocity=100),
            scale_type=ScaleType.MAJOR
        )

    def test_get_roman_numeral_from_chord_MAJOR(self) -> None:
        chord = Chord(
            root=Note(note_name="C", octave=4, duration=1, velocity=100),
            quality=ChordQuality.MAJOR
        )
        result = RomanNumeral.get_roman_numeral_from_chord(chord, self.scale)
        self.assertEqual(result.numeral, "I")
        self.assertEqual(result.quality, ChordQuality.MAJOR)

    def test_from_scale_degree_MINOR(self) -> None:
        for degree, expected in [(1, "i"), (2, "ii"), (3, "iii"), (4, "iv"), (5, "v"), (6, "vi"), (7, "vii")]:
            with self.subTest(degree=degree):
                numeral = RomanNumeral.from_scale_degree(degree, ChordQuality.MINOR)
                self.assertEqual(numeral.numeral.lower(), expected)
                self.assertEqual(numeral.quality, ChordQuality.MINOR)

    def test_from_scale_degree_diminished(self) -> None:
        numeral = RomanNumeral.from_scale_degree(3, ChordQuality.DIMINISHED)
        self.assertEqual(numeral.numeral, "iii°")
        self.assertEqual(numeral.quality, ChordQuality.DIMINISHED)

    def test_from_scale_degree_augmented(self) -> None:
        numeral = RomanNumeral.from_scale_degree(4, ChordQuality.AUGMENTED)
        self.assertEqual(numeral.numeral, "IV+")
        self.assertEqual(numeral.quality, ChordQuality.AUGMENTED)

    def test_from_scale_degree_MINOR_7(self) -> None:
        numeral = RomanNumeral.from_scale_degree(2, ChordQuality.MINOR_SEVENTH)
        self.assertEqual(numeral.numeral, "ii7")
        self.assertEqual(numeral.quality, ChordQuality.MINOR_SEVENTH)

    def test_from_scale_degree_MAJOR_7(self) -> None:
        numeral = RomanNumeral.from_scale_degree(1, ChordQuality.MAJOR_SEVENTH)
        self.assertEqual(numeral.numeral, "Imaj7")
        self.assertEqual(numeral.quality, ChordQuality.MAJOR_SEVENTH)

    def test_from_scale_degree_dominant_7(self) -> None:
        numeral = RomanNumeral.from_scale_degree(5, ChordQuality.DOMINANT_SEVENTH)
        self.assertEqual(numeral.numeral, "V7")
        self.assertEqual(numeral.quality, ChordQuality.DOMINANT_SEVENTH)

    def test_from_scale_degree_invalid_degree(self) -> None:
        with self.assertRaises(ValueError):
            RomanNumeral.from_scale_degree(0, ChordQuality.MAJOR)
        with self.assertRaises(ValueError):
            RomanNumeral.from_scale_degree(8, ChordQuality.MAJOR)

    def test_to_scale_degree_valid(self) -> None:
        test_cases = [
            ("I", ChordQuality.MAJOR, 1),
            ("ii", ChordQuality.MINOR, 2),
            ("iii", ChordQuality.MINOR, 3),
            ("IV", ChordQuality.MAJOR, 4),
            ("v", ChordQuality.MINOR, 5),
            ("vi", ChordQuality.MINOR, 6),
            ("vii", ChordQuality.MINOR, 7),
        ]
        for numeral_str, quality, expected_degree in test_cases:
            with self.subTest(numeral=numeral_str):
                numeral = RomanNumeral(numeral=numeral_str, quality=quality)
                result = RomanNumeral.to_scale_degree(numeral)
                self.assertEqual(result, expected_degree)

    def test_to_scale_degree_invalid(self):
        """Test invalid Roman numerals raise ValueError."""
        invalid_numerals = ["viii", "ixv", "iix"]
        for numeral in invalid_numerals:
            with self.assertRaises(ValueError):
                roman = RomanNumeral(numeral=numeral, quality=ChordQuality.MAJOR)
                roman.to_scale_degree()  # This should raise the ValueError

    def test_get_roman_numeral_from_chord_different_degrees(self) -> None:
        test_cases = [
            (Note(note_name="D", octave=4, duration=1, velocity=100), ChordQuality.MINOR, "ii"),
            (Note(note_name="E", octave=4, duration=1, velocity=100), ChordQuality.DIMINISHED, "iii°"),
            (Note(note_name="A", octave=4, duration=1, velocity=100), ChordQuality.MINOR_SEVENTH, "vi7"),
        ]
        
        for root_note, quality, expected_numeral in test_cases:
            with self.subTest(root=root_note.note_name, quality=quality):
                chord = Chord(root=root_note, quality=quality)
                result = RomanNumeral.get_roman_numeral_from_chord(chord, self.scale)
                self.assertEqual(result.numeral, expected_numeral)
                self.assertEqual(result.quality, quality)

    def test_get_roman_numeral_from_chord_note_not_in_scale(self) -> None:
        scale = FakeScale(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)
        chord = Chord(root=Note(note_name="C#", octave=4, duration=1, velocity=100), quality=ChordQuality.MAJOR)
        with self.assertRaises(ValueError) as cm:
            RomanNumeral.get_roman_numeral_from_chord(chord, scale)
        self.assertIn("not in scale", str(cm.exception))

    def test_get_roman_numeral_from_chord_unexpected_error(self) -> None:
        scale = FakeScale(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)
        chord = Chord(root=Note(note_name="C", octave=4, duration=1, velocity=100), quality=ChordQuality.MAJOR)

        with patch.object(FakeScale, 'get_degree_of_note', side_effect=TypeError("Simulating an unexpected error.")):
            with self.assertRaises(ValueError) as cm:
                RomanNumeral.get_roman_numeral_from_chord(chord, scale)
            self.assertIsInstance(cm.exception.__cause__, TypeError)
            self.assertIn("Unexpected error processing chord", str(cm.exception))


if __name__ == "__main__":
    unittest.main()