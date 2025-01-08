"""Module for handling sequences of musical notes."""

from typing import List, Optional, Sequence, Union, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.note_gen.models.musical_elements import Note
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.scale import Scale
from src.note_gen.models.note_event import NoteEvent


class NoteSequence(BaseModel):
    """A sequence of musical notes."""

    notes: List[Union[Note, int]] = Field(description="List of notes")
    events: List[NoteEvent] = Field(
        default_factory=list, description="List of note events"
    )
    duration: float = Field(default=0.0, description="Duration of the note sequence")
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode='before')
    def check_notes_field(cls, values: dict[str, Any]) -> dict[str, Any]:
        notes = values.get('notes')
        if notes is not None:
            validated = []
            for note in notes:
                if isinstance(note, (Note, int)):
                    validated.append(note)
                else:
                    raise ValueError(f"Invalid note type: {type(note)}")
            values['notes'] = validated
        return values

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: List[Union[Note, int]]) -> List[Note]:
        validated_notes = []
        for note in v:
            if isinstance(note, int):
                validated_notes.append(Note.from_midi(note))
            elif isinstance(note, Note):
                validated_notes.append(note)
            else:
                raise ValueError("All notes must be instances of Note.")
        return validated_notes

    @field_validator("events", mode="before")
    def check_events(cls, value: List[NoteEvent]) -> List[NoteEvent]:
        """Validate that all events are instances of NoteEvent."""
        if not all(isinstance(event, NoteEvent) for event in value):
            raise ValueError("All events must be NoteEvent instances.")
        return value

    def add_note(
        self,
        note: Union[str, Note, int],
        position: float = 0.0,
        duration: float = 1.0,
        velocity: int = 100,
        semitones: int = 0,
    ) -> None:
        """Add a note to the sequence."""
        if isinstance(note, Note):
            transposed_note = note.transpose(semitones)
            event = NoteEvent(
                note=transposed_note, position=position, duration=duration, velocity=velocity
            )
        elif isinstance(note, int):
            note = Note.from_midi(note)
            event = NoteEvent(
                note=note, position=position, duration=duration, velocity=velocity
            )
        else:
            raise TypeError("Invalid note type")
        self.events.append(event)  

    def _update_duration(self) -> None:
        if self.events:
            self.duration = max(event.end_position for event in self.events)

    def get_notes_at(self, position: float) -> List[NoteEvent]:
        """Get all notes active at the given position."""
        return [
            event
            for event in self.events
            if event.position <= position < event.end_position
        ]

    def clear(self) -> None:
        """Clear all notes from the sequence."""
        self.events.clear()
        self.duration = 0.0

    def transpose(self, semitones: int) -> None:
        """Transpose the note sequence by the given number of semitones."""
        print(f"Transposing NoteSequence with events: {[event.note for event in self.events]}")
        for event in self.events:
            if isinstance(event.note, Note):
                print(f"Before transposition: {event.note}")
                event.note.transpose(semitones)
                print(f"After transposition: {event.note}")
            elif isinstance(event.note, int):
                # Handle int case appropriately, if needed
                pass
            else:
                raise TypeError("Invalid note type in NoteSequence.")