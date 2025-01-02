"""Tests for note sequence models."""

import pytest
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.note_sequence import NoteSequence

def test_note_sequence_creation() -> None:
    """Test valid note sequence creation."""
    valid_sequence = NoteSequence(notes=[60, 62, 64, 65])
    expected_notes = [
        Note.from_midi(60),
        Note.from_midi(62),
        Note.from_midi(64),
        Note.from_midi(65)
    ]
    assert [note.midi_number for note in valid_sequence.notes] == [60, 62, 64, 65]
    assert valid_sequence.notes == expected_notes


def test_note_sequence_validation() -> None:
    """Test validation of note sequence."""
    with pytest.raises(ValueError):
        NoteSequence(notes=["invalid"])


def test_musical_operations() -> None:
    """Test musical operations."""
    sequence = NoteSequence(notes=[60, 62, 64])
    transposed_sequence = sequence.transpose(2)  # Transpose up by 2 semitones
    expected_notes = [
        Note.from_midi(62),
        Note.from_midi(64),
        Note.from_midi(66)
    ]
    assert [note.midi_number for note in transposed_sequence.notes] == [62, 64, 66]
    assert transposed_sequence.notes == expected_notes