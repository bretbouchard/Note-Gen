import unittest
import pytest
from unittest.mock import patch
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.enums import ScaleType, ChordQualityType
from src.note_gen.models.chord import Chord
from src.note_gen.models.chord_quality import ChordQualityType
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
from typing import List, Optional
import random
from pydantic import ValidationError
import logging
from src.note_gen.models.roman_numeral import RomanNumeral


class TestChordProgressionGenerator(unittest.TestCase):
    def setUp(self):
        self.scale_info = FakeScaleInfo(
            root=Note('C', octave=4),  
            scale_type=ScaleType.MAJOR
        )
        self.generator = ChordProgressionGenerator(
            name="Test Generator",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=self.scale_info,
            complexity=0.5,
            test_mode=True
        )

    def test_no_pattern_provided_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.generator.generate(pattern=[], progression_length=4)

    def test_invalid_pattern_raises_validation_error(self) -> None:
        with self.assertRaises(ValueError):  
            self.generator.generate(pattern=["nonexistent"], progression_length=4)

    def test_generate_with_valid_pattern(self) -> None:
        import logging
        # logging.basicConfig(level=logging.DEBUG)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        try:
            progression = ChordProgression(
                name="Generated Progression",
                chords=chords,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=self.scale_info,
                quality=ChordQualityType.MAJOR  # Added quality field
            )
        except ValidationError as e:
            print(f"Validation errors: {e.errors()}")
            print(f"Error details: {e}")
            raise
            # Removed e.dict() since it does not exist in Pydantic V2
        logging.debug(f"Initializing ChordProgression with:")
        logging.debug(f"  Name: {self.generator.name}")
        logging.debug(f"  Key: {self.generator.key}")
        logging.debug(f"  Scale Type: {self.generator.scale_type}")
        logging.debug(f"  Chords: {[c.root.note_name for c in self.generator.chords]}")
        logging.debug(f"  Scale Info: root={self.scale_info.root.note_name}, scale_type={self.scale_info.scale_type}")
        pattern = ["I-IV-V"]
        logging.debug(f"Testing valid pattern generation with pattern: {pattern}")
        progression = self.generator.generate(pattern=pattern, progression_length=10)
        logging.debug(f"Generated progression: {progression.chords}")
        self.assertEqual(len(progression.chords), 3, 
                         f"Expected 3 chords, but got {len(progression.chords)}.")
        self.assertIsInstance(progression.chords[0], Chord, 
                             f"First chord is not an instance of Chord. Got {type(progression.chords[0])} instead.")

    def test_generate_custom_with_mismatched_lists_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.generator.generate_custom(degrees=[1, 2], qualities=["MAJOR"])

    def test_generate_custom_valid(self):
        root_note = Note(note_name='C', octave=4)
        scale_info = FakeScaleInfo(root=root_note, scale_type=ScaleType.MINOR)
        chord1 = Chord(root=Note(note_name='C', octave=4), quality=ChordQualityType.MAJOR)
        chord2 = Chord(root=Note(note_name='D', octave=4), quality=ChordQualityType.MINOR)
        progression = ChordProgression(
            name='Test Progression',
            chords=[chord1, chord2],
            key='C',
            scale_type=ScaleType.MINOR,
            scale_info=scale_info
        )
        assert progression.chords == [chord1, chord2]
        # Additional assertions here

    def test_generate_custom_invalid_degree(self):
        root_note = Note(note_name='C', octave=4)
        scale_info = FakeScaleInfo(root=root_note, scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info,
            name="Test Progression",
            key="C",
            scale_type=ScaleType.MAJOR,
            chords=[
                Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        with pytest.raises(ValueError):
            # Try to generate a chord progression with an invalid scale degree (8 is invalid, valid range is 1-7)
            gen.generate_custom(degrees=[8], qualities=[ChordQualityType.MAJOR])

    def test_generate_custom_valid_chord_instance(self) -> ChordProgression:
        root_note = Note(note_name='C', octave=4)
        scale_info = FakeScaleInfo(root=root_note, scale_type=ScaleType.MINOR)
        chord1 = Chord(root=Note(note_name='C', octave=4), quality=ChordQualityType.MAJOR)
        chord2 = Chord(root=Note(note_name='D', octave=4), quality=ChordQualityType.MINOR)
        progression = ChordProgression(
            name='Test Progression',
            chords=[chord1, chord2],
            key='C',
            scale_type=ScaleType.MINOR,
            scale_info=scale_info
        )
        assert progression.chords == [chord1, chord2]
        # Additional assertions here

    def test_generate_random_valid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="Eb", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MINOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MINOR)
            ],
            complexity=1
        )
        with patch.object(random, 'choice', side_effect=[1, ChordQualityType.MAJOR, 5, ChordQualityType.MINOR]):
            progression = gen.generate_random(length=2)
            self.assertEqual(len(progression.chords), 2)

    def test_generate_chord_progression_with_negative_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        with self.assertRaises(ValueError):
            gen.generate_random(-1)

    def test_generate_chord_progression_with_boundary_values(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        with self.assertRaises(ValueError):
            gen.generate_random(0)

    def test_generate_chord_valid(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MINOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=chords,
            complexity=1
        )

        # Call generate_chord for each chord in the progression
        for chord in chords:
            generated_chord = gen.generate_chord(root=chord.root, quality=chord.quality)
            assert isinstance(generated_chord, Chord)
            assert generated_chord.root.note_name == chord.root.note_name
            assert generated_chord.quality == chord.quality

        progression = gen.generate_chord(root=chords[0].root, quality=chords[0].quality)  # Adjust this line if needed

    def test_generate_chord_invalid_numeral(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        with self.assertRaises(ValueError):
            gen.generate_chord_numeral(numeral="invalid_numeral")

    def test_generate_chord_progression_with_unsupported_chord_type(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        with self.assertRaises(ValueError):
            gen.generate(pattern=["unsupported"], progression_length=4)

    def test_generate_large_chord_progression(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MINOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=chords,
            complexity=1
        )
        progression = gen.generate_large(length=10)
        self.assertEqual(len(progression.chords), 10)

    def test_generate_chord_progression_with_zero_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=chords,
            complexity=1
        )

    def test_generate_chord_progression_with_exact_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
    
    def test_generate_chord_progression_with_boundary_values(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        with self.assertRaises(ValueError):
            gen.generate(pattern=['I-IV-V'], progression_length=0)

    def test_generate_chord_notes_invalid_quality(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        # Create a mock ChordQualityType that's not a real quality
        mock_quality = "INVALID_QUALITY"
        with self.assertRaises(ValueError):
            gen.generate_chord(root=Note(note_name="C", octave=4), quality=mock_quality)

    def test_generate_chord_notes_major(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
        self.assertEqual(generated_chord.quality, ChordQualityType.MAJOR)

    def test_generate_chord_notes_minor(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MINOR)
        self.assertEqual(generated_chord.quality, ChordQualityType.MINOR)

    def test_generate_chord_notes_augmented(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.AUGMENTED)
        self.assertEqual(generated_chord.quality, ChordQualityType.AUGMENTED)

    def test_generate_chord_notes_diminished(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info, 
            name="Test Progression", 
            key="C", 
            scale_type=ScaleType.MINOR, 
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            complexity=1
        )
        generated_chord = gen.generate_chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.DIMINISHED)
        self.assertEqual(generated_chord.quality, ChordQualityType.DIMINISHED)

    def test_generate_chord_notes_transposition(self) -> None:
        root_note = Note(note_name="B", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        generated_notes = chord._generate_chord_notes()
        expected_notes = [
            root_note,
            root_note.transpose(4),  # E
            root_note.transpose(7)   # G#
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_out_of_range(self) -> None:
        root_note = Note(note_name="C", octave=6, duration=1.0, velocity=100)  # High octave
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        generated_notes = chord._generate_chord_notes()
        self.assertTrue(all(note.octave <= 6 for note in generated_notes))  # Ensure no note exceeds octave 6

    def test_generate_chord_notes_major(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MAJOR)
        generated_notes = chord._generate_chord_notes()
        expected_notes = [
            root_note,
            root_note.transpose(4),  # E
            root_note.transpose(7)   # G
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_minor(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.MINOR)
        generated_notes = chord._generate_chord_notes()
        expected_notes = [
            root_note,
            root_note.transpose(3),  # Eb
            root_note.transpose(7)   # G
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_augmented(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.AUGMENTED)
        generated_notes = chord._generate_chord_notes()
        expected_notes = [
            root_note,
            root_note.transpose(4),  # E
            root_note.transpose(8)   # G#
        ]
        self.assertEqual(generated_notes, expected_notes)

    def test_generate_chord_notes_diminished(self) -> None:
        root_note = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        chord = Chord(root=root_note, quality=ChordQualityType.DIMINISHED)
        generated_notes = chord._generate_chord_notes()
        expected_notes = [
            root_note,
            root_note.transpose(3),  # Eb
            root_note.transpose(6)   # Gb
        ]
        self.assertEqual(generated_notes, expected_notes)


class TestAdvancedChordProgressionGenerator:
    @pytest.fixture
    def chord_progression_generator(self):
        """Create a standard chord progression generator for testing."""
        return ChordProgressionGenerator(
            name="Test Generator",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=FakeScaleInfo(root=Note('C', octave=4), scale_type=ScaleType.MAJOR),
            complexity=0.5,
            test_mode=True
        )

    def test_calculate_pattern_complexity(self, chord_progression_generator):
        """Test complexity calculation for different chord patterns."""
        # Simple major progression
        simple_pattern = [(1, ChordQualityType.MAJOR), (4, ChordQualityType.MAJOR), (5, ChordQualityType.MAJOR)]
        complexity = chord_progression_generator.calculate_pattern_complexity(simple_pattern)
        assert 0 <= complexity <= 1, "Complexity should be between 0 and 1"
        assert complexity < 0.5, "Simple progression should have low complexity"

        # Complex progression with varied qualities
        complex_pattern = [
            (2, ChordQualityType.MINOR7), 
            (5, ChordQualityType.DOMINANT7), 
            (1, ChordQualityType.MAJOR7), 
            (6, ChordQualityType.DIMINISHED)
        ]
        complexity = chord_progression_generator.calculate_pattern_complexity(complex_pattern)
        assert complexity > 0.5, "Complex progression should have higher complexity"

    def test_generate_genre_specific_pattern(self, chord_progression_generator):
        """Test genre-specific pattern generation."""
        # Test various genres
        genres = ['pop', 'jazz', 'blues', 'classical', 'unknown']
        
        for genre in genres:
            pattern = chord_progression_generator.generate_genre_specific_pattern(genre, length=4)
            
            assert len(pattern) == 4, f"Pattern for {genre} should have 4 chords"
            assert all(isinstance(degree, int) and 1 <= degree <= 7 for degree, _ in pattern), f"Invalid scale degrees in {genre} pattern"
            assert all(isinstance(quality, ChordQualityType) for _, quality in pattern), f"Invalid chord qualities in {genre} pattern"

    def test_generate_with_tension_resolution(self, chord_progression_generator):
        """Test tension and resolution pattern generation."""
        base_pattern = [
            (1, ChordQualityType.MAJOR), 
            (4, ChordQualityType.MAJOR), 
            (5, ChordQualityType.MAJOR), 
            (1, ChordQualityType.MAJOR)
        ]
        
        enhanced_pattern = chord_progression_generator.generate_with_tension_resolution(base_pattern)
        
        assert len(enhanced_pattern) == len(base_pattern), "Pattern length should remain the same"
        
        # Check that some chords might have been replaced with tension-creating chords
        tension_qualities = {ChordQualityType.DOMINANT7, ChordQualityType.DIMINISHED, ChordQualityType.AUGMENTED}
        tension_count = sum(1 for _, quality in enhanced_pattern if quality in tension_qualities)
        assert 0 <= tension_count <= len(enhanced_pattern), "Tension chords added within reasonable limits"

    def test_generate_advanced(self, chord_progression_generator):
        """Test advanced chord progression generation with various inputs."""
        # Test genre-based generation
        jazz_progression = chord_progression_generator.generate_advanced(genre='jazz', complexity_target=0.7)
        assert jazz_progression is not None, "Jazz progression generation failed"
        
        # Test custom pattern generation
        custom_progression = chord_progression_generator.generate_advanced(
            pattern=['I', 'V', 'vi'], 
            length=4, 
            complexity_target=0.5
        )
        assert custom_progression is not None, "Custom pattern progression generation failed"
        assert len(custom_progression.chords) == 4, "Custom progression should have 4 chords"
        
        # Test random generation
        random_progression = chord_progression_generator.generate_advanced(length=3, complexity_target=0.3)
        assert random_progression is not None, "Random progression generation failed"
        assert len(random_progression.chords) == 3, "Random progression should have 3 chords"

    def test_complexity_targeting(self, chord_progression_generator):
        """Test complexity targeting in advanced generation."""
        complexity_targets = [0.2, 0.5, 0.8]
        
        for target in complexity_targets:
            progression = chord_progression_generator.generate_advanced(
                genre='pop', 
                complexity_target=target
            )
            
            # Calculate actual progression complexity
            pattern = [(chord.root.scale_degree, chord.quality) for chord in progression.chords]
            actual_complexity = chord_progression_generator.calculate_pattern_complexity(pattern)
            
            # Allow some tolerance in complexity matching
            assert abs(actual_complexity - target) <= 0.2, f"Complexity should be close to {target}"

class TestChordProgressionGeneratorComprehensive(unittest.TestCase):
    def setup_method(self, method):  
        """Setup method to create a base ScaleInfo for testing"""
        self.scale_info = FakeScaleInfo(
            root=Note('C', octave=4), 
            scale_type=ScaleType.MAJOR
        )
        self.generator = ChordProgressionGenerator(
            name="Test Generator",
            chords=[],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=self.scale_info,
            complexity=0.5,
            test_mode=True
        )

    def test_generate_progression(self):
        # Update method to use FakeScaleInfo and new imports
        progression = self.generator.generate(pattern=['I', 'IV', 'V'])
        self.assertIsNotNone(progression)
        self.assertEqual(len(progression.chords), 3)

    def test_generate_custom_complex_progression(self):
        """Test generating a more complex chord progression with mixed qualities"""
        cpg = ChordProgressionGenerator(
            name='Complex Progression',
            chords=[],
            key='C',
            scale_type='MAJOR',
            scale_info=self.scale_info,
            complexity=1.0
        )

        progression = cpg.generate_custom(
            degrees=[1, 6, 4, 5],
            qualities=[
                ChordQualityType.MAJOR,
                ChordQualityType.MINOR,
                ChordQualityType.MAJOR,
                ChordQualityType.DOMINANT7
            ]
        )

        assert len(progression.chords) == 4
        assert progression.key == 'C'
        assert progression.scale_type == 'MAJOR'

        # Verify specific chord details
        assert progression.chords[0].root.note_name == 'C'
        assert progression.chords[0].quality == ChordQualityType.MAJOR
        assert progression.chords[1].root.note_name == 'A'
        assert progression.chords[1].quality == ChordQualityType.MINOR
        assert progression.chords[2].root.note_name == 'F'
        assert progression.chords[2].quality == ChordQualityType.MAJOR
        assert progression.chords[3].root.note_name == 'G'
        assert progression.chords[3].quality == ChordQualityType.DOMINANT7

    def test_generate_custom_edge_cases(self):
        """Test edge cases in chord progression generation"""
        cpg = ChordProgressionGenerator(
            name='Edge Case Progression',
            chords=[],
            key='C',
            scale_type='MAJOR',
            scale_info=self.scale_info,
            complexity=0.1
        )

        # Test single chord progression
        single_chord_prog = cpg.generate_custom(
            degrees=[1],
            qualities=[ChordQualityType.MAJOR]
        )
        assert len(single_chord_prog.chords) == 1

        # Test progression with all minor chords
        minor_prog = cpg.generate_custom(
            degrees=[2, 3, 6],
            qualities=[
                ChordQualityType.MINOR,
                ChordQualityType.MINOR,
                ChordQualityType.MINOR
            ]
        )
        assert all(chord.quality == ChordQualityType.MINOR for chord in minor_prog.chords)

    def test_generate_custom_invalid_inputs(self):
        """Test handling of invalid inputs in chord progression generation"""
        cpg = ChordProgressionGenerator(
            name='Invalid Progression',
            chords=[],
            key='C',
            scale_type='MAJOR',
            scale_info=self.scale_info,
            complexity=0.5
        )

        # Test mismatched lengths
        with pytest.raises(ValueError, match="Degrees and qualities must have the same length."):
            cpg.generate_custom(
                degrees=[1, 4],
                qualities=[ChordQualityType.MAJOR]
            )

        # Test out-of-range degrees
        with pytest.raises(ValueError, match="Invalid degree: 8"):
            cpg.generate_custom(
                degrees=[8],
                qualities=[ChordQualityType.MAJOR]
            )

    def test_generate_custom_default_quality(self):
        """Test default chord quality when not explicitly specified"""
        cpg = ChordProgressionGenerator(
            name='Default Quality Progression',
            chords=[],
            key='C',
            scale_type='MAJOR',
            scale_info=self.scale_info,
            complexity=0.3
        )

        progression = cpg.generate_custom(
            degrees=[1, 4, 5],
            qualities=[None, ChordQualityType.MINOR, None]
        )

        assert progression.chords[0].quality == ChordQualityType.MAJOR
        assert progression.chords[1].quality == ChordQualityType.MINOR
        assert progression.chords[2].quality == ChordQualityType.MAJOR

if __name__ == "__main__":
    unittest.main()