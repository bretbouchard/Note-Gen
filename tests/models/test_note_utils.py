"""Tests for note utility functions."""

import pytest
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.enums import AccidentalType
from src.note_gen.models.note_utils import calculate_midi_note, get_note, create_note, update_note, delete_note, midi_to_note, note_name_to_midi, validate_note_name


def test_get_note() -> None:
    """Test get_note function."""
    note = Note.from_name('C4')
    assert note.note_name == 'C'
    assert note.octave == 4

def test_create_note() -> None:
    """Test create_note function."""
    note = Note.from_name('C4')
    assert note.note_name == 'C'
    assert note.octave == 4


def test_update_note() -> None:
    """Test update_note function."""
    note = Note.from_name('C4')
    updated_note = update_note(note, 'D', 4)
    assert updated_note.note_name == 'D'
    assert updated_note.octave == 4


def test_delete_note() -> None:
    """Test delete_note function."""
    note = Note.from_name('C4')
    assert delete_note(note) is None