"""Module for handling sequences of musical notes."""

from typing import List, Union, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, field_validator, Field, model_validator

from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.note_event import NoteEvent


class NoteSequence(BaseModel):
    """A sequence of musical notes or events."""
    notes: List[Union[Note, int]]
    events: List[NoteEvent] = Field(default_factory=list)
    duration: float = 0.0
    default_duration: float = 1.0

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        validate_assignment=True
    )

    @property
    def total_duration(self) -> float:
        """Calculate the total duration of the notes in the sequence."""
        return sum(note.duration for note in self.notes if isinstance(note, Note))

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, value: List[Union[Note, int]]) -> List[Union[Note, int]]:
        """Validate and convert notes."""
        result = []
        for note in value:
            if isinstance(note, int):
                # Convert MIDI number to Note
                if not (0 <= note <= 127):
                    raise ValueError(f"Invalid MIDI number: {note}")
                result.append(Note.from_midi(note))
            elif isinstance(note, Note):
                result.append(note)
            else:
                raise ValueError(f"Invalid note type: {type(note)}")
        return result

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, value: float) -> float:
        """Validate duration is non-negative."""
        if value < 0:
            raise ValueError("Duration must be non-negative")
        return value

    def add_note(self, note: Union[Note, int], position: float = 0.0, duration: float = 1.0, velocity: int = 100) -> None:
        """Add a note to the sequence at the specified position."""
        if isinstance(note, int):
            note = Note.from_midi(note, duration=duration, velocity=velocity)
        event = NoteEvent(note=note, position=position, duration=duration, velocity=velocity)
        self.events.append(event)

    def get_notes_at(self, position: float) -> List[Note]:
        """Get all notes at a specific position."""
        return [event.note for event in self.events if event.position == position]

    def clear(self) -> None:
        """Clear all notes and events from the sequence."""
        self.notes = []
        self.events = []
        self.duration = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert the sequence to a dictionary."""
        return {
            "notes": [note.to_dict() if isinstance(note, Note) else note for note in self.notes],
            "events": [event.to_dict() for event in self.events],
            "duration": self.duration
        }


class SimpleNoteSequence(BaseModel):
    """Model for a sequence of notes."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    notes: List[Note] = Field(default_factory=list, description="List of notes in the sequence")
    
    def add_note(self, note: Note) -> None:
        """Add a note to the sequence."""
        self.notes.append(note)
    
    def get_note_at(self, index: int) -> Note:
        """Get note at specified index."""
        return self.notes[index]
    
    def __len__(self) -> int:
        return len(self.notes)
    
    def __str__(self) -> str:
        return f"NoteSequence(notes={[str(note) for note in self.notes]})"