import unittest
from unittest.mock import patch
from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType, ScaleType
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from typing import List, Optional
import random
from pydantic import ValidationError
import logging

class TestChordProgressionGenerator(unittest.TestCase):
    def test_no_pattern_provided_raises_error(self) -> None:
        scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):
            gen.generate(pattern=[], progression_length=4)

    def test_invalid_pattern_raises_validation_error(self) -> None:
        scale_info = ScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):  
            gen.generate(pattern=["nonexistent"], progression_length=4)

    def test_generate_with_valid_pattern(self) -> None:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        try:
            gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=chords)
            progression = ChordProgression(
                name="Generated Progression",
                chords=chords,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=scale_info,
                quality=ChordQualityType.MAJOR  # Added quality field
            )
        except ValidationError as e:
            print(f"Validation errors: {e.errors()}")
            print(f"Error details: {e}")
            raise
            # Removed e.dict() since it does not exist in Pydantic V2
        logging.debug(f"Initializing ChordProgression with:")
        logging.debug(f"  Name: {gen.name}")
        logging.debug(f"  Key: {gen.key}")
        logging.debug(f"  Scale Type: {gen.scale_type}")
        logging.debug(f"  Chords: {[c.root.note_name for c in gen.chords]}")
        logging.debug(f"  Scale Info: root={scale_info.root.note_name}, scale_type={scale_info.scale_type}")
        pattern = ["I-IV-V"]
        logging.debug(f"Testing valid pattern generation with pattern: {pattern}")
        progression = gen.generate(pattern=pattern, progression_length=10)
        logging.debug(f"Generated progression: {progression.chords}")
        self.assertEqual(len(progression.chords), 3, 
                         f"Expected 3 chords, but got {len(progression.chords)}.")
        self.assertIsInstance(progression.chords[0], Chord, 
                             f"First chord is not an instance of Chord. Got {type(progression.chords[0])} instead.")

    def test_generate_custom_with_mismatched_lists_raises_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):
            gen.generate_custom(degrees=[1, 2], qualities=["MAJOR"])

    def test_generate_custom_valid(self) -> ChordProgression:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=chords)
        progression = gen.generate_custom(degrees=[1, 2], qualities=[ChordQualityType.MAJOR, ChordQualityType.MINOR])
        self.assertEqual(progression.name, "Generated Progression")
        self.assertEqual(len(progression.chords), 2)
        self.assertEqual(progression.chords[0].quality, ChordQualityType.MAJOR)
        self.assertEqual(progression.chords[1].quality, ChordQualityType.MINOR)
        return progression

    def test_generate_random_valid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with patch.object(random, 'choice', side_effect=[1, ChordQualityType.MAJOR, 3, ChordQualityType.MINOR]):
            progression = gen.generate_random(length=2)
            self.assertEqual(len(progression.chords), 2)

    def test_generate_random_invalid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=chords)
        with self.assertRaises(ValueError):
            gen.generate_random(length=-1)

    def test_generate_chord_valid(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=chords)

        # Call generate_chord for each chord in the progression
        for chord in chords:
            generated_chord = gen.generate_chord(root=chord.root, quality=chord.quality)
            assert isinstance(generated_chord, Chord)
            assert generated_chord.root.note_name == chord.root.note_name
            assert generated_chord.quality == chord.quality

        progression = gen.generate_chord(root=chords[0].root, quality=chords[0].quality)  # Adjust this line if needed

    def test_generate_chord_invalid_numeral(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):
            gen.generate_chord_numeral(numeral="invalid_numeral")

    def test_generate_chord_progression_with_negative_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=-1)

    def test_generate_chord_progression_with_unsupported_chord_type(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):
            gen.generate(pattern=["unsupported"], progression_length=4)

    def test_generate_large_chord_progression(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=chords)
        progression = gen.generate_large(length=10)
        self.assertEqual(len(progression.chords), 10)

    def test_generate_chord_progression_with_zero_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=chords)

    def test_generate_chord_progression_with_exact_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
    
    def test_generate_chord_progression_with_boundary_values(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_notes_invalid_quality(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        with self.assertRaises(ValueError):
            gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.INVALID_QUALITY)

    def test_generate_chord_notes_major(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
        self.assertEqual(generated_chord.quality, ChordQualityType.MAJOR)

    def test_generate_chord_notes_minor(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MINOR)
        self.assertEqual(generated_chord.quality, ChordQualityType.MINOR)

    def test_generate_chord_notes_augmented(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.AUGMENTED)
        self.assertEqual(generated_chord.quality, ChordQualityType.AUGMENTED)

    def test_generate_chord_notes_diminished(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(scale_info=scale_info, name="Test Progression", key="C", scale_type=ScaleType.MAJOR, chords=[
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ])
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.DIMINISHED)
        self.assertEqual(generated_chord.quality, ChordQualityType.DIMINISHED)

    def test_generate_chord_notes_transposition(self) -> None:
        root_note = Note(note_name="B", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        generated_notes = chord._generate_chord_notes(root=root_note, quality=ChordQualityType.MAJOR)
        expected_notes = [
            root_note,
            root_note.transpose(4),  # E
            root_note.transpose(7)   # G#
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_out_of_range(self) -> None:
        root_note = Note(note_name="C", octave=6, duration=1.0, velocity=100)  # High octave
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        generated_notes = chord._generate_chord_notes(root=root_note, quality=ChordQualityType.MAJOR)
        self.assertTrue(all(note.octave <= 6 for note in generated_notes))  # Ensure no note exceeds octave 6

    def test_generate_chord_notes_major(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        generated_notes = chord._generate_chord_notes(root=root_note, quality=ChordQualityType.MAJOR)
        expected_notes = [
            root_note,
            root_note.transpose(4),  # E
            root_note.transpose(7)   # G
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_minor(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MINOR)
        generated_notes = chord._generate_chord_notes(root=root_note, quality=ChordQualityType.MINOR)
        expected_notes = [
            root_note,
            root_note.transpose(3),  # Eb
            root_note.transpose(7)   # G
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_augmented(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.AUGMENTED)
        generated_notes = chord._generate_chord_notes(root=root_note, quality=ChordQualityType.AUGMENTED)
        expected_notes = [
            root_note,
            root_note.transpose(4),  # E
            root_note.transpose(8)   # G#
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_diminished(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.DIMINISHED)
        generated_notes = chord._generate_chord_notes(root=root_note, quality=ChordQualityType.DIMINISHED)
        expected_notes = [
            root_note,
            root_note.transpose(3),  # Eb
            root_note.transpose(6)   # Gb
        ]
        self.assertEqual(generated_notes, expected_notes)

if __name__ == "__main__":
    unittest.main()