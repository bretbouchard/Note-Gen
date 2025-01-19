import unittest
from unittest.mock import patch
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale import ScaleType
from src.note_gen.models.chord_progression import ChordProgression
import random
import logging

logger = logging.getLogger(__name__)

class FakeScaleInfo(ScaleInfo):
    scale_type: ScaleType = ScaleType.MAJOR
    root: Note = Note(note_name="C", octave=4, duration=1, velocity=64, stored_midi_number=60)
    key: str = 'C'

    def __init__(self, root: Note = Note(note_name='C', octave=4, duration=1, velocity=64, stored_midi_number=60), scale_type: ScaleType = ScaleType.MAJOR):
        super().__init__(root=root, scale_type=scale_type)

    def get_scale_degree_note(self, degree: int) -> Note:
        notes = ["C", "D", "E", "F", "G", "A", "B"]
        return Note(note_name=notes[degree - 1], octave=4, stored_midi_number=60 + degree - 1, duration=1, velocity=64)

    def get_chord_quality_for_degree(self, degree: int) -> str:
        return "major" if degree % 2 == 1 else "minor"

    def get_scale_notes(self) -> list[Note]:
        return [Note(note_name="C", octave=4, stored_midi_number=60, duration=1, velocity=64), Note(note_name="D", octave=4, stored_midi_number=62, duration=1, velocity=64), Note(note_name="E", octave=4, stored_midi_number=64, duration=1, velocity=64)]

    def get_scale_note_at_degree(self, degree: int) -> Note:
        notes = [
            Note(note_name='C', octave=4, stored_midi_number=60, duration=1, velocity=64),
            Note(note_name='D', octave=4, stored_midi_number=62, duration=1, velocity=64),
            Note(note_name='E', octave=4, stored_midi_number=64, duration=1, velocity=64),
            Note(note_name='F', octave=4, stored_midi_number=65, duration=1, velocity=64),
            Note(note_name='G', octave=4, stored_midi_number=67, duration=1, velocity=64),
            Note(note_name='A', octave=4, stored_midi_number=69, duration=1, velocity=64),
            Note(note_name='B', octave=4, stored_midi_number=71, duration=1, velocity=64)
        ]
        if 1 <= degree <= len(notes):
            return notes[degree - 1]
        raise ValueError(f"Invalid scale degree: {degree}")

    def get_chord_quality_for(self, degree: int) -> str:
        return "major" if degree % 2 == 1 else "minor"


class TestChordProgressionGenerator(unittest.TestCase):
    def test_no_pattern_provided_raises_error(self) -> None:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate(pattern=[], progression_length=4)


    def test_invalid_pattern_raises_validation_error(self) -> None:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):  # Update expectation to ValueError
            gen.generate(pattern=["nonexistent"], progression_length=4)

    def test_generate_with_valid_pattern(self) -> None:
        scale_info = FakeScaleInfo()
        # Use a known pattern from PROGRESSION_PATTERNS: "I-IV-V"
        gen = ChordProgressionGenerator(scale_info=scale_info)
        pattern = ["I-IV-V"]
        logger.debug(f"Testing valid pattern generation with pattern: {pattern}")
        progression = gen.generate(pattern=pattern, progression_length=10)
        logger.debug(f"Generated progression: {progression.chords}")
        logger.debug(f"Pattern being tested: {pattern}")
        logger.debug(f"Generated progression: {progression.chords}")
        self.assertEqual(len(progression.chords), 10)
        self.assertIsInstance(progression.chords[0], Chord)

    def test_generate_custom_with_mismatched_lists_raises_error(self) -> None:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate_custom(degrees=[1, 2], qualities=["major"])

    def test_generate_custom_valid(self) -> ChordProgression:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        progression = gen.generate_custom(degrees=[1, 2], qualities=["major", "minor"])
        self.assertEqual(len(progression.chords), 2)
        self.assertEqual(progression.chords[0].quality, ChordQualityType.MAJOR)
        self.assertEqual(progression.chords[1].quality, ChordQualityType.MINOR)
        return progression

    def test_generate_random_valid_length(self) -> None:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        # Patch random.choice to control output
        with patch.object(random, 'choice', side_effect=[1, "major", 3, "minor"]):
            progression = gen.generate_random(length=2)
            self.assertEqual(len(progression.chords), 2)

    def test_generate_random_invalid_length(self) -> None:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate_random(length=-1)

    def test_generate_chord_valid(self) -> None:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        chord = gen.generate_chord("i")  # maps to scale_degree=1 (see RomanNumeral code)
        # In FakeScaleInfo, 1 -> "C"
        self.assertEqual(chord.root.note_name, "C")
        self.assertEqual(chord.quality, ChordQualityType.MAJOR)  # Because get_chord_quality_for_degree(1) -> 'major'

    def test_generate_chord_invalid_numeral(self) -> None:
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        with self.assertRaises(ValueError):
            gen.generate_chord("random-numeral")

    def test_generate_chord_progression_with_negative_length(self) -> None:
        with self.assertRaises(ValueError):
            ChordProgressionGenerator(scale_info=FakeScaleInfo()).generate(pattern=['I-IV-V'], progression_length=-1)

    def test_generate_chord_progression_with_unsupported_chord_type(self) -> None:
        with self.assertRaises(ValueError):
            ChordProgressionGenerator(scale_info=FakeScaleInfo()).generate(pattern=['unsupported'], progression_length=4)

    def test_generate_large_chord_progression(self) -> None:
        progression = ChordProgressionGenerator(scale_info=FakeScaleInfo()).generate(pattern=['I-IV-V'], progression_length=10)
        self.assertEqual(len(progression.chords), 10)

    def test_generate_chord_progression_with_boundary_values(self) -> None:
        with self.assertRaises(ValueError):
            ChordProgressionGenerator(scale_info=FakeScaleInfo()).generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_progression_with_zero_length(self) -> None:
        # Test for zero length progression raises ValueError
        with self.assertRaises(ValueError):
            ChordProgressionGenerator(scale_info=FakeScaleInfo()).generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_progression_with_exact_length(self) -> None:
        # Test for exact match of generated chords to progression length
        progression = ChordProgressionGenerator(scale_info=FakeScaleInfo()).generate(pattern=['I-IV-V'], progression_length=3)
        self.assertEqual(len(progression.chords), 3)

    def test_generate_random_with_edge_case(self) -> None:
        # Test random generation with a length of 1
        scale_info = FakeScaleInfo()
        gen = ChordProgressionGenerator(scale_info=scale_info)
        progression = gen.generate_random(length=1)
        self.assertEqual(len(progression.chords), 1)
        self.assertIsInstance(progression.chords[0], Chord)

    def test_generate_large_progression_with_repeated_patterns(self) -> None:
        # Test large progression with repeated patterns
        progression = ChordProgressionGenerator(scale_info=FakeScaleInfo()).generate(pattern=['I-IV-V', 'I-IV-V'], progression_length=6)
        self.assertEqual(len(progression.chords), 6)
        self.assertIsInstance(progression.chords[0], Chord)
        self.assertIsInstance(progression.chords[1], Chord)
        self.assertIsInstance(progression.chords[2], Chord)
        self.assertIsInstance(progression.chords[3], Chord)
        self.assertIsInstance(progression.chords[4], Chord)
        self.assertIsInstance(progression.chords[5], Chord)

    def test_chord_inversions(self) -> None:
        # Test for a C major chord in root position
        scale_info = ScaleInfo(root=Note(note_name="C", octave=4, stored_midi_number=60, duration=1, velocity=100), scale_type="major")
        chords = [
            Chord(root=Note(note_name="C", octave=4, stored_midi_number=60, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, stored_midi_number=65, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, stored_midi_number=67, duration=1.0, velocity=100), quality=ChordQualityType.DOMINANT_7)
        ]
        progression = ChordProgressionGenerator(scale_info=scale_info, chords=chords)
        notes = progression.generate_chord_notes(chords[0].root, chords[0].quality, chords[0].inversion)
        print(f"Root position notes: {notes}")  # Debug output
        assert notes == [Note(note_name="C", octave=4, stored_midi_number=60, duration=1.0, velocity=100), Note(note_name="E", octave=4, stored_midi_number=64, duration=1.0, velocity=100), Note(note_name="G", octave=4, stored_midi_number=67, duration=1.0, velocity=100)], "Root position notes do not match"

        chord = Chord(root=Note(note_name="C", octave=4, stored_midi_number=60, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR, inversion=1)
        notes = progression.generate_chord_notes(chord.root, chord.quality, chord.inversion)
        print(f"First inversion notes: {notes}")  # Debug output
        assert notes == [Note(note_name="E", octave=4, stored_midi_number=64, duration=1.0, velocity=100), Note(note_name="G", octave=4, stored_midi_number=67, duration=1.0, velocity=100), Note(note_name="C", octave=5, stored_midi_number=72, duration=1.0, velocity=100)], "First inversion notes do not match"

        chord = Chord(root=Note(note_name="C", octave=4, stored_midi_number=60, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR, inversion=2)
        notes = progression.generate_chord_notes(chord.root, chord.quality, chord.inversion)
        print(f"Second inversion notes: {notes}")  # Debug output
        assert notes == [Note(note_name="G", octave=4, stored_midi_number=67, duration=1.0, velocity=100), Note(note_name="C", octave=5, stored_midi_number=72, duration=1.0, velocity=100), Note(note_name="E", octave=5, stored_midi_number=76, duration=1.0, velocity=100)], "Second inversion notes do not match"

    def test_generate_chord_progression_with_pattern(self) -> None:
        pattern = ['I-IV-V']  # Define a valid pattern using Roman numerals
        scale_info = FakeScaleInfo()  # Ensure scale_info is defined properly
        gen = ChordProgressionGenerator(scale_info=scale_info)
        progression = gen.generate(pattern=pattern, progression_length=3)
        assert progression is not None, "Progression should not be None"
        self.assertEqual(len(progression.chords), 3)
        self.assertIsInstance(progression.chords[0], Chord)
        self.assertIsInstance(progression.chords[1], Chord)
        self.assertIsInstance(progression.chords[2], Chord)

    def test_create_chord(self):
        root_note = Note(note_name="C", octave=4, stored_midi_number=60, duration=1, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        self.assertEqual(chord.root, root_note)

    def test_invalid_quality(self):
        root_note = Note(note_name="C", octave=4, stored_midi_number=60, duration=1, velocity=100)
        invalid_quality = "invalid_quality"  # Invalid value
        with self.assertRaises(ValueError):
            Chord(root=root_note, quality=invalid_quality)

    def test_invalid_root(self):
        class InvalidNote:
            note_name = "InvalidNoteName"
            octave = 4
            duration = 1
            velocity = 100

        with self.assertRaises(ValueError):
            Chord(root=InvalidNote(), quality=ChordQualityType.MAJOR)

    def test_create_chord_valid(self):
        root_note = Note(note_name="C", octave=4, stored_midi_number=60, duration=1, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        assert chord.root == root_note

    def test_create_chord_invalid_quality(self):
        root_note = Note(note_name="C", octave=4, stored_midi_number=60, duration=1, velocity=100)
        invalid_quality = "invalid_quality"  # Invalid value
        with self.assertRaises(ValueError):
            Chord(root=root_note, quality=invalid_quality)

    def test_create_chord_invalid_root(self):
        class InvalidNote:
            note_name = "InvalidNoteName"
            octave = 4
            duration = 1
            velocity = 100

        with self.assertRaises(ValueError):
            Chord.from_quality(root=InvalidNote(), quality=ChordQualityType.MAJOR)

if __name__ == "__main__":
    unittest.main()