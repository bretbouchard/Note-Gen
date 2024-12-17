import pytest
from models.note_sequence import NoteSequence
from models.note import Note


def test_note_sequence_creation():
    sequence = NoteSequence()
    assert sequence is not None


def test_note_sequence_add_note():
    sequence = NoteSequence()
    note = Note(note_name="C", midi_number=60)
    sequence.add_note(note)
    assert sequence.get_notes_at(0) == [note]


def test_note_sequence_clear():
    sequence = NoteSequence()
    note = Note(note_name="C", midi_number=60)
    sequence.add_note(note)
    sequence.clear()
    assert sequence.get_notes_at(0) == []  # Should be empty after clear
