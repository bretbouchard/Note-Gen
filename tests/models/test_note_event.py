from __future__ import annotations
import pytest
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.note import Note
from pydantic_core import ValidationError


def test_create_note_event() -> None:
    note = Note.from_name("C4")
    event = NoteEvent(note=note, position=0.0, duration=1.0)
    assert event.note == note
    assert event.position == 0.0
    assert event.duration == 1.0


def test_invalid_position() -> None:
    note = Note.from_name("C4")
    with pytest.raises(ValidationError) as exc_info:
        NoteEvent(note=note, position=-1.0)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'greater_than_equal'
    assert errors[0]['loc'] == ('position',)


def test_invalid_duration() -> None:
    note = Note.from_name("C4")
    with pytest.raises(ValidationError) as exc_info:
        NoteEvent(note=note, duration=-1.0)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'greater_than'
    assert errors[0]['loc'] == ('duration',)


def test_invalid_velocity() -> None:
    note = Note.from_name("C4")
    with pytest.raises(ValidationError) as exc_info:
        NoteEvent(note=note, velocity=130)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'less_than_equal'
    assert errors[0]['loc'] == ('velocity',)


def test_note_event_creation_with_velocity() -> None:
    """Test creation of a NoteEvent with a specific velocity."""
    note = Note.from_name("C4")
    event = NoteEvent(note=note, position=0.0, duration=1.0, velocity=100)
    assert event.velocity == 100


def test_note_event_negative_duration() -> None:
    """Test that negative duration raises an error."""
    note = Note.from_name("C4")
    with pytest.raises(ValidationError) as exc_info:
        NoteEvent(note=note, position=0.0, duration=-1.0)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'greater_than'
    assert errors[0]['loc'] == ('duration',)