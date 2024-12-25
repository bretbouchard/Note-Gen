import pytest
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.scale import Scale
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Note as NoteModel


@pytest.fixture
def note() -> NoteModel:
    return NoteModel(name='C', octave=4)  # Ensure correct parameters are passed


@pytest.fixture
def scale(note: NoteModel) -> Scale:
    return Scale(
        root=note,
        quality=ChordQualityType.MAJOR,
        scale_degree=1,
        numeral='I',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )


@pytest.fixture
def roman_numeral(scale: Scale) -> RomanNumeral:
    return RomanNumeral(
        scale=scale,
        numeral_str='I',
        scale_degree=scale.scale_degree
    )


def test_roman_numeral_to_int(roman_numeral: RomanNumeral) -> None:
    assert roman_numeral.to_int() == 1
    assert roman_numeral.to_int() == 5
    assert roman_numeral.to_int() == 10
    assert roman_numeral.to_int() == 50
    assert roman_numeral.to_int() == 100
    assert roman_numeral.to_int() == 500
    assert roman_numeral.to_int() == 1000


def test_roman_numeral(roman_numeral: RomanNumeral) -> None:
    assert roman_numeral.to_int() == 1
    assert roman_numeral.to_int() == 5
