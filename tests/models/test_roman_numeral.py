"""Test roman numeral."""

import pytest
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.scale import Scale


@pytest.fixture
def scale() -> Scale:
    root_note = Note.from_name("C4")
    return Scale(root=root_note, quality='major')


def test_roman_numeral_to_int() -> None:
    """Test converting roman numeral to integer."""
    assert RomanNumeral.to_int("I") == 1
    assert RomanNumeral.to_int("IV") == 4
    assert RomanNumeral.to_int("V") == 5
    assert RomanNumeral.to_int("VII") == 7


def test_roman_numeral() -> None:
    """Test roman numeral class."""
    roman = RomanNumeral("I")
    assert roman.numeral == "I"
    assert roman.to_int() == 1
