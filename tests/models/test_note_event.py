import pytest
from src.note_gen.models.note import Note
from src.note_gen.models.note_event import NoteEvent
from pydantic import ValidationError, root_validator, field_validator

def test_create_note_event() -> None:
    note = Note.from_name("C4")
    event = NoteEvent(note=note, position=0.0, duration=1.0)
    assert event.note == note
    assert event.position == 0.0
    assert event.duration == 1.0


def test_invalid_position() -> None:
    note = Note.from_name("C4")
    with pytest.raises(ValueError, match="Position cannot be negative."):
        NoteEvent(note=note, position=-1.0)


def test_invalid_duration() -> None:
    note = Note.from_name("C4")
    with pytest.raises(ValueError, match="Duration must be positive."):
        NoteEvent(note=note, duration=-1.0)


def test_invalid_velocity() -> None:
    note = Note.from_name("C4")
    with pytest.raises(ValidationError, match=r"Value error, MIDI velocity must be between 0 and 127."):
        NoteEvent(note=note, velocity=130)

def test_note_event_creation_with_velocity() -> None:
    """Test creation of a NoteEvent with a specific velocity."""
    note = Note.from_name("C4")
    event = NoteEvent(note=note, position=0.0, duration=1.0, velocity=100)
    assert event.velocity == 100

def test_note_event_negative_duration() -> None:
    """Test that negative duration raises an error."""
    note = Note.from_name("C4")
    with pytest.raises(ValueError, match="Duration must be positive"):
        NoteEvent(note=note, position=0.0, duration=-1.0)