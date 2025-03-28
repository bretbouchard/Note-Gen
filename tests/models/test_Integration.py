from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note_event import NoteEvent
from pydantic import BaseModel, Field, field_validator

def test_chord_with_note_event_integration() -> None:
    """Test that a chord's notes can be used to create NoteEvents."""
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQuality.DOMINANT)  # Updated to use ChordQuality enum

    events = [
        NoteEvent(note=note, position=i * 0.5, duration=0.5)
        for i, note in enumerate(chord.notes)
    ]
    assert len(events) == len(chord.notes)
    assert isinstance(events[0].note, Note)  # Ensure note is of type Note
    assert events[0].note.note_name == chord.notes[0].note_name
    assert events[1].position == 0.5