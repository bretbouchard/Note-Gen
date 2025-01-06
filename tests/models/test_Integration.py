from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.enums import ChordQualityType

def test_chord_with_note_event_integration() -> None:
    """Test that a chord's notes can be used to create NoteEvents."""
    root_note = Note.from_name("C4")
    chord = Chord(root=root_note, quality=ChordQualityType.DOMINANT)
    events = [
        NoteEvent(note=note, position=i * 0.5, duration=0.5)
        for i, note in enumerate(chord.notes)
    ]
    assert len(events) == len(chord.notes)
    assert events[0].note.note_name == "C"
    assert events[1].position == 0.5