import pytest
from models.note import Note


def test_note_creation():
    note = Note(note_name="C", midi_number=60)
    assert note.note_name == "C"
    assert note.midi_number == 60


def test_note_equality():
    note1 = Note(note_name="C", midi_number=60)
    note2 = Note(note_name="C", midi_number=60)
    assert note1 == note2


def test_note_invalid_midi():
    with pytest.raises(ValueError):
        Note(note_name="C", midi_number=128)  # MIDI number out of range
