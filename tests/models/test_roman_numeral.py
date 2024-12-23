import pytest
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.scale import Scale, ScaleInfo
from src.note_gen.models.note import Note  # Added import for Note class


@pytest.fixture
def note():
    return Note(name='C', accidental='', octave=4)  # Ensure correct parameters are passed


@pytest.fixture
def roman_numeral(note):
    scale = Scale(
        scale=ScaleInfo(root=note),
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
        inversion=0
    )
    return RomanNumeral(
        scale=scale,
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )


def test_roman_numeral_to_int(roman_numeral) -> None:
    assert roman_numeral.to_int("I") == 1
    assert roman_numeral.to_int("V") == 5
    assert roman_numeral.to_int("X") == 10
    assert roman_numeral.to_int("L") == 50
    assert roman_numeral.to_int("C") == 100
    assert roman_numeral.to_int("D") == 500
    assert roman_numeral.to_int("M") == 1000

def test_roman_numeral(roman_numeral) -> None:
    assert roman_numeral.to_int("I") == 1
    assert roman_numeral.to_int("V") == 5
