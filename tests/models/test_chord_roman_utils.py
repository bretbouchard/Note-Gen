from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.scale import Scale, ScaleInfo
from src.note_gen.models.chord_roman_utils import get_roman_numeral_from_chord, get_chord_from_roman_numeral
from src.note_gen.models.enums import ChordQualityType  # Ensure ChordQualityType is imported
import pytest

@pytest.fixture
def note():
    return Note(name='C', octave=4)

@pytest.fixture
def chord(note):
    return Chord(root=note, quality=ChordQualityType.MAJOR)

@pytest.fixture
def roman_numeral(note: Note) -> RomanNumeral:
    scale = Scale(
        scale_info_v2=ScaleInfo(root=note.scale("major")),
        numeral='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )
    return RomanNumeral(scale=scale, numeral='I', numeral_str='I', scale_degree=1)

def test_get_roman_numeral_from_chord(chord: Chord) -> None:
    assert get_roman_numeral_from_chord(chord) == "I"

def test_get_chord_from_roman_numeral(roman_numeral: RomanNumeral, note: Note) -> None:
    assert get_chord_from_roman_numeral(roman_numeral, note) == "Cmaj7"