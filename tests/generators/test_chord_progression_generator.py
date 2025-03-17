import pytest
from unittest.mock import patch
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.patterns import ChordProgression
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.roman_numeral import RomanNumeral
import random
from pydantic import ValidationError
import logging


class TestChordProgressionGenerator:
    def setup_method(self):
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
        with pytest.raises(ValueError):
            self.generator.generate(pattern=[], progression_length=4)

    def test_invalid_pattern_raises_validation_error(self) -> None:
        with pytest.raises(ValueError):
            self.generator.generate(pattern=["nonexistent"], progression_length=4)

    def test_generate_with_valid_pattern(self) -> None:
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
        ]
        try:
            progression = ChordProgression(
                name="Generated Progression",
                chords=chords,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=self.scale_info,
                quality=ChordQuality.MAJOR
            )
        except ValidationError as e:
            logging.error(f"Validation errors: {e.errors()}")
            raise

        pattern = ["I-IV-V"]
        progression = self.generator.generate(pattern=pattern, progression_length=10)
        assert len(progression.chords) == 3
        assert isinstance(progression.chords[0], Chord)

    def test_generate_custom_with_mismatched_lists_raises_error(self) -> None:
        with pytest.raises(ValueError):
            self.generator.generate_custom(degrees=[1, 2], qualities=[ChordQuality.MAJOR])

    def test_generate_custom_valid(self):
        root_note = Note(note_name='C', octave=4)
        scale_info = FakeScaleInfo(root=root_note, scale_type=ScaleType.MINOR)
        chord1 = Chord(root=Note(note_name='C', octave=4), quality=ChordQuality.MAJOR)
        chord2 = Chord(root=Note(note_name='D', octave=4), quality=ChordQuality.MINOR)
        progression = ChordProgression(
            name='Test Progression',
            chords=[chord1, chord2],
            key='C',
            scale_type=ScaleType.MINOR,
            scale_info=scale_info
        )
        assert progression.chords == [chord1, chord2]

    def test_generate_custom_invalid_degree(self):
        root_note = Note(note_name='C', octave=4)
        scale_info = FakeScaleInfo(root=root_note, scale_type=ScaleType.MAJOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info,
            name="Test Progression",
            key="C",
            scale_type=ScaleType.MAJOR,
            chords=[
                Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR)
            ],
            complexity=1
        )
        with pytest.raises(ValueError):
            gen.generate_custom(degrees=[8], qualities=[ChordQuality.MAJOR])

    def test_generate_random_valid_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=64), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info,
            name="Test Progression",
            key="C",
            scale_type=ScaleType.MINOR,
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="Eb", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MINOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MINOR)
            ],
            complexity=1
        )
        with patch.object(random, 'choice', side_effect=[1, ChordQuality.MAJOR, 5, ChordQuality.MINOR]):
            progression = gen.generate_random(length=2)
            assert len(progression.chords) == 2

    def test_generate_chord_progression_with_negative_length(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info,
            name="Test Progression",
            key="C",
            scale_type=ScaleType.MINOR,
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
            ],
            complexity=1
        )
        with pytest.raises(ValueError):
            gen.generate_random(-1)

    def test_generate_chord_progression_with_boundary_values(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type=ScaleType.MINOR)
        gen = ChordProgressionGenerator(
            scale_info=scale_info,
            name="Test Progression",
            key="C",
            scale_type=ScaleType.MINOR,
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
            ],
            complexity=1
        )
        with pytest.raises(ValueError):
            gen.generate_random(0)

    def test_calculate_pattern_complexity(self):
        simple_pattern = [(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR), (5, ChordQuality.MAJOR)]
        complexity = ChordProgressionGenerator.calculate_pattern_complexity(simple_pattern)
        assert 0 <= complexity <= 1
        assert complexity < 0.5

        complex_pattern = [
            (2, ChordQuality.MINOR_SEVENTH),
            (5, ChordQuality.DOMINANT_SEVENTH),
            (1, ChordQuality.MAJOR_SEVENTH),
            (6, ChordQuality.DIMINISHED)
        ]
        complex_complexity = ChordProgressionGenerator.calculate_pattern_complexity(complex_pattern)
        assert 0 <= complex_complexity <= 1
        assert complex_complexity > 0.5


if __name__ == "__main__":
    pytest.main()