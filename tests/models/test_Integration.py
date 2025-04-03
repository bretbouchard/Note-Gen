import pytest
from note_gen.models.note import Note
from note_gen.models.chord import Chord
from note_gen.models.note_event import NoteEvent
from note_gen.core.enums import ChordQuality

def test_chord_with_note_event_integration():
    """Test that a chord's notes can be used to create NoteEvents."""
    # Create root note
    root_note = Note.from_name("C4")
    
    # Create chord with explicit quality
    chord = Chord(root="C", quality=ChordQuality.MAJOR)
    
    # Generate the notes for the chord
    chord.get_notes()  # This will call _generate_notes() if notes are not yet generated
    
    # Create note events from chord notes
    events = [
        NoteEvent(
            note=note,
            position=i * 0.5,
            duration=0.5
        )
        for i, note in enumerate(chord.notes)
    ]
    
    # Verify events
    assert len(events) == len(chord.notes)
    assert isinstance(events[0].note, Note)
    assert events[0].note.note_name == chord.notes[0].note_name
    assert events[1].position == 0.5
    assert all(event.duration == 0.5 for event in events)
