import pytest
from unittest.mock import patch
from pydantic import BaseModel, ValidationError, Field, ConfigDict
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.patterns import ChordProgressionPattern, ChordPatternItem
from src.note_gen.core.enums import ScaleType

# Rebuild the model to finalize forward references
ChordProgression.model_rebuild()

@pytest.fixture
def basic_generator():
    scale_info = ScaleInfo(
        root=Note(note_name="C", octave=4),
        scale_type=ScaleType.MAJOR,
        key="C"
    )
    return ChordProgressionGenerator(
        name="Test Progression",
        chords=[
            Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="G", octave=4), quality=ChordQuality.MAJOR)
        ],
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        complexity=0.5
    )

def test_generate_with_tension_resolution(basic_generator):
    base_pattern = [(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR)]
    result = basic_generator.generate_with_tension_resolution(base_pattern)
    assert len(result) > 0
    assert all(isinstance(item[0], int) for item in result)
    assert all(isinstance(item[1], ChordQuality) for item in result)

def test_generate_genre_specific_pattern(basic_generator):
    for genre in ['pop', 'jazz', 'blues', 'classical']:
        pattern = basic_generator.generate_genre_specific_pattern(genre)
        assert len(pattern) == 4
        assert all(isinstance(item[0], int) and isinstance(item[1], (str, ChordQuality)) for item in pattern)

def test_generate_custom_invalid_degrees(basic_generator):
    with pytest.raises(ValueError, match="Invalid degree"):
        basic_generator.generate_custom([0, 8], [ChordQuality.MAJOR, ChordQuality.MAJOR])

def test_generate_custom_valid(basic_generator):
    progression = basic_generator.generate_custom(
        [1, 4, 5],
        [ChordQuality.MAJOR, ChordQuality.MAJOR, ChordQuality.MAJOR]
    )
    assert len(progression.chords) == 3
    assert progression.key == "C"
    assert progression.scale_type == ScaleType.MAJOR

def test_generate_large(basic_generator):
    length = 8
    progression = basic_generator.generate_large(length)
    assert len(progression.chords) == length
    assert all(isinstance(chord, Chord) for chord in progression.chords)

def test_generate_large_invalid_length(basic_generator):
    with pytest.raises(ValueError, match="Length must be greater than 0"):
        basic_generator.generate_large(0)

def test_generate_progression_for_pattern(basic_generator):
    pattern = ChordProgressionPattern(
        name="Test Pattern",
        chords=[
            ChordPatternItem(chord_name="C", duration=1.0, degree=1, quality=ChordQuality.MAJOR),
            ChordPatternItem(chord_name="F", duration=1.0, degree=4, quality=ChordQuality.MAJOR)
        ]
    )
    progression = basic_generator.generate_progression_for_pattern(pattern)
    assert len(progression.chords) == 2
    assert progression.key == "C"

def test_calculate_pattern_complexity():
    scale_type = ScaleType.MAJOR  # Use enum instead of string
    # Rest of the test...
