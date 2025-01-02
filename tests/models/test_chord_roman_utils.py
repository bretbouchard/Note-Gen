"""Test chord roman utils."""

import pytest
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale import Scale
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.chord_roman_utils import get_roman_numeral_from_chord, get_chord_from_roman_numeral
from src.note_gen.models.enums import ChordQualityType  # Ensure ChordQualityType is imported

@pytest.fixture
def note():
    return Note.from_name('C4')

@pytest.fixture
def chord(note):
    return Chord(root=note, notes=[note], quality=ChordQualityType.MAJOR)

@pytest.fixture
def scale() -> Scale:
    root_note = Note.from_name("C4")
    scale_degree = 1  # Use an integer for scale degree
    return Scale(
        root=root_note,
        quality="major",
        scale_degree=scale_degree,
        numeral="I",
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )  # Create a Scale instance

@pytest.fixture
def roman_numeral(note: Note, scale) -> RomanNumeral:
    return RomanNumeral(scale=scale, numeral='I', numeral_str='I', scale_degree=1)

def test_get_roman_numeral_from_chord(chord: Chord) -> None:
    assert get_roman_numeral_from_chord(chord) == "I"

def test_get_chord_from_roman_numeral(roman_numeral: RomanNumeral, note: Note) -> None:
    assert get_chord_from_roman_numeral(roman_numeral, note) == "Cmaj7"

def test_get_roman_numeral_from_chord(note) -> None:
    """Test get_roman_numeral_from_chord function."""
    scale = Scale(root=note, quality='major')
    chord = scale.get_chord_at(0)  # I chord
    roman_numeral = get_roman_numeral_from_chord(chord, scale)
    assert roman_numeral == 'I'

def test_get_chord_from_roman_numeral(note) -> None:
    """Test get_chord_from_roman_numeral function."""
    scale = Scale(root=note, quality='major')
    chord = get_chord_from_roman_numeral('I', scale)
    assert chord.root.note_name == 'C'
    assert chord.root.octave == '4'
    assert chord.quality == 'major'