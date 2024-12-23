import pytest
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.note import Note


def test_note_sequence_creation() -> None:
    """Test valid note sequence creation."""
    valid_sequence = NoteSequence(notes=[60, 62, 64, 65])
    assert valid_sequence.notes == [60, 62, 64, 65]


def test_note_sequence_validation() -> None:
    """Test note sequence validation."""
    with pytest.raises(ValueError):
        NoteSequence(notes=[60, 62, 128])  # 128 is out of MIDI range
    with pytest.raises(ValueError):
        NoteSequence(notes=[-1])  # -1 is out of MIDI range


def test_musical_operations() -> None:
    """Test musical operations."""
    sequence = NoteSequence(notes=[60, 62, 64])
    transposed_sequence = sequence.transpose(2)  # Transpose up by 2 semitones
    assert transposed_sequence.notes == [62, 64, 66]