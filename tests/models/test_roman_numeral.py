import pytest
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.scale import Scale
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Note as NoteModel
from src.note_gen.models.scale_degree import ScaleDegree


@pytest.fixture
def note() -> NoteModel:
    return NoteModel(name='C', octave=4)  # Ensure correct parameters are passed


@pytest.fixture
def scale() -> Scale:
    root_note = NoteModel(name="C", accidental="", octave=4)
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
def roman_numeral(scale: Scale) -> RomanNumeral:
    return RomanNumeral(
        numeral_str='I',
        scale_degree=scale.scale_degree,
        scale=scale,
        numeral='I'  # Ensure the numeral is passed
    )


def test_roman_numeral_to_int(roman_numeral: RomanNumeral) -> None:
    assert roman_numeral.to_int() == 1  # Corrected expected value


def test_roman_numeral(roman_numeral: RomanNumeral) -> None:
    assert roman_numeral.to_int() == 1  # Corrected expected value
