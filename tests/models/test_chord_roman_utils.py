from src.note_gen.models.chord import Chord, ChordQualityType
from src.note_gen.models.note import Note
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.scale import Scale, ScaleInfo
from src.note_gen.models.chord_roman_utils import get_roman_numeral_from_chord, get_chord_from_roman_numeral
import pytest

@pytest.fixture
def note():
    return Note(name='C', accidental='', octave=4)

@pytest.fixture
def chord(note):
    return Chord(root=note, quality=ChordQualityType.MAJOR, bass=note)

@pytest.fixture
def roman_numeral(note):
    scale = Scale(
        scale=ScaleInfo(root=note.scale("major")),
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0,
        is_altered=False,
        is_suspended=False,
        is_extended=False,
        is_add=False,
        is_app=False,
        is_alt=False,
        is_bass=False,
        is_root=False,
        is_third=False,
        is_fifth=False,
        is_seventh=False,
        is_ninth=False,
        is_eleventh=False,
        is_thirteenth=False
    )
    return RomanNumeral(scale=scale, numeral='I', numeral_str='I', scale_degree=1, is_major=True, is_diminished=False, is_augmented=False, is_half_diminished=False, has_seventh=False, has_ninth=False, has_eleventh=False, inversion=0)

def test_get_roman_numeral_from_chord(chord: Chord) -> None:
    assert get_roman_numeral_from_chord(chord) == "I"

def test_get_chord_from_roman_numeral(roman_numeral: RomanNumeral, note: Note) -> None:
    assert get_chord_from_roman_numeral(roman_numeral, note) == "Cmaj7"