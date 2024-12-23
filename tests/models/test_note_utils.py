import pytest
from src.note_gen.models.note_utils import calculate_midi_note, midi_to_note, note_name_to_midi, validate_note_name, midi_to_note_name
from src.note_gen.models.note import AccidentalType, Note


def test_get_note() -> None:
    assert midi_to_note(60) == "C4"  

def test_create_note() -> None:
    assert note_name_to_midi("C4") == 60  

def test_update_note() -> None:
    assert calculate_midi_note("C", AccidentalType.NATURAL, 4) == 48  

def test_delete_note() -> None:
    assert validate_note_name("C4") == True  

@pytest.fixture
def note():
    return Note(name='C', accidental='', octave=4)  

@pytest.fixture
def note():
    return Note(name='C', accidental='', octave=4)  