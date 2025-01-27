import unittest
from unittest.mock import patch
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType, ScaleType
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale import Scale
from src.note_gen.models.chord_progression import ChordProgression
import random
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class FakeScaleInfo(ScaleInfo):
    scale_type: ScaleType = ScaleType.MAJOR
    root: Note

    def __init__(self, root: Optional[Note] = None, scale_type: Optional[ScaleType] = ScaleType.MAJOR):
        super().__init__(root=root or Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=scale_type)



    def get_note_for_degree(self, degree: int) -> Optional[Note]:
        if degree < 1 or degree > 7:
            return None
        scale = Scale(root=self.root, scale_type=self.scale_type)
        notes = scale.get_notes()
        return notes[degree - 1] if notes else None

    def get_scale_note_at_degree(self, degree: int) -> Note:
        scale = Scale(root=self.root, scale_type=self.scale_type)
        return scale.get_note_at_degree(degree)

    def get_chord_quality_for_degree(self, degree: int) -> ChordQualityType:
        if degree < 1 or degree > 7:
            raise ValueError("Degree must be between 1 and 7")
        return ChordQualityType.MAJOR if degree % 2 == 1 else ChordQualityType.MINOR

    def get_scale_degree_note(self, degree: int) -> Note:
        notes = ["C", "D", "E", "F", "G", "A", "B"]
        return Note(note_name=notes[degree - 1], octave=4, duration=1, velocity=64)

    def get_scale_notes(self) -> List[Note]:
        return [
            Note(note_name="C", octave=4, duration=1, velocity=64),
            Note(note_name="D", octave=4, duration=1, velocity=64),
            Note(note_name="E", octave=4, duration=1, velocity=64)
        ]

    def get_chord_quality_for(self, degree: int) -> ChordQualityType:
        return ChordQualityType.MAJOR if degree % 2 == 1 else ChordQualityType.MINOR


class TestChordProgressionGenerator(unittest.TestCase):
    def test_no_pattern_provided_raises_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=[], progression_length=4)

    def test_invalid_pattern_raises_validation_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):  
            gen.generate(pattern=["nonexistent"], progression_length=4)

    def test_generate_with_valid_pattern(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        pattern = ["I-IV-V"]
        logger.debug(f"Testing valid pattern generation with pattern: {pattern}")
        progression = gen.generate(pattern=pattern, progression_length=10)
        logger.debug(f"Generated progression: {progression.chords}")
        logger.debug(f"Pattern being tested: {pattern}")
        logger.debug(f"Generated progression: {progression.chords}")
        self.assertEqual(len(progression.chords), 10)
        self.assertIsInstance(progression.chords[0], Chord)

    def test_generate_custom_with_mismatched_lists_raises_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate_custom(degrees=[1, 2], qualities=["major"])

    def test_generate_custom_valid(self) -> ChordProgression:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate_custom(degrees=[1, 2], qualities=["major", "minor"])
        self.assertEqual(len(progression.chords), 2)
        self.assertEqual(progression.chords[0].quality, ChordQualityType.MAJOR)
        self.assertEqual(progression.chords[1].quality, ChordQualityType.MINOR)
        return progression

    def test_generate_random_valid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with patch.object(random, 'choice', side_effect=[1, "major", 3, "minor"]):
            progression = gen.generate_random(length=2)
            self.assertEqual(len(progression.chords), 2)

    def test_generate_random_invalid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate_random(length=-1)

    def test_generate_chord_valid(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        chord = gen.generate_chord("i")  
        self.assertEqual(chord.root.note_name, "C")
        self.assertEqual(chord.quality, ChordQualityType.MAJOR)  

    def test_generate_chord_invalid_numeral(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate_chord_numeral(numeral="invalid_numeral")

    def test_generate_chord_progression_with_negative_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=-1)

    def test_generate_chord_progression_with_unsupported_chord_type(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['unsupported'], progression_length=4)

    def test_generate_large_chord_progression(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        progression = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR).generate(pattern=['I-IV-V'], progression_length=10)
        self.assertEqual(len(progression.chords), 10)

    def test_generate_chord_progression_with_boundary_values(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_progression_with_zero_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_progression_with_exact_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate(pattern=['I-IV-V'], progression_length=3)
        self.assertEqual(len(progression.chords), 3)

    def test_generate_random_with_edge_case(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate_random(length=1)
        self.assertEqual(len(progression.chords), 1)

    def test_generate_large_progression_with_repeated_patterns(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        progression = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR).generate(pattern=['I-IV-V', 'I-IV-V'], progression_length=6)
        self.assertEqual(len(progression.chords), 6)

    def test_chord_inversions(self) -> None:
        scale_info = ScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.DOMINANT_7)
        ]
        progression = ChordProgressionGenerator(scale_info=scale_info, chords=chords, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)

    def test_generate_chord_progression_with_pattern(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate(pattern=['I-IV-V'], progression_length=4)
        assert progression is not None, "Progression should not be None"
        self.assertEqual(len(progression.chords), 4)
        self.assertIsInstance(progression.chords[0], Chord)
        self.assertIsInstance(progression.chords[1], Chord)
        self.assertIsInstance(progression.chords[2], Chord)
        self.assertIsInstance(progression.chords[3], Chord)

    def test_create_chord(self):
        root_note = Note(note_name="C", octave=4, duration=1, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        self.assertEqual(chord.root, root_note)

    def test_invalid_quality(self):
        root_note = Note(note_name="C", octave=4, duration=1, velocity=100)
        invalid_quality = "invalid_quality"  
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
        root_note = Note(note_name="C", octave=4, duration=1, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        assert chord.root == root_note

    def test_create_chord_invalid_quality(self):
        root_note = Note(note_name="C", octave=4, duration=1, velocity=100)
        invalid_quality = "invalid_quality"  
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

    def test_invalid_pattern_raises_validation_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=["unsupported"], progression_length=4)

    def test_generate_chord_invalid_numeral(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate_chord_numeral(numeral="invalid_numeral")

    def test_generate_chord_progression_with_boundary_values(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_progression_with_exact_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate(pattern=['I-IV-V'], progression_length=3)
        self.assertEqual(len(progression.chords), 3)

    def test_generate_chord_progression_with_negative_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=-1)

    def test_generate_chord_progression_with_pattern(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate(pattern=['I-IV-V'], progression_length=4)
        self.assertEqual(len(progression.chords), 4)

    def test_generate_chord_invalid_numeral(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate_chord_numeral(numeral="invalid_numeral")

    def test_generate_chord_progression_with_boundary_values(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_progression_with_exact_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate(pattern=['I-IV-V'], progression_length=3)
        self.assertEqual(len(progression.chords), 3)

    def test_generate_chord_progression_with_negative_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=-1)

    def test_generate_chord_progression_with_pattern(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        progression = gen.generate(pattern=['I-IV-V'], progression_length=4)
        self.assertEqual(len(progression.chords), 4)

    def test_generate_chord_progression_with_unsupported_chord_type(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64))
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            gen.generate(pattern=["unsupported"], progression_length=4)

if __name__ == "__main__":
    unittest.main()