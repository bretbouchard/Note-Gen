"""Module for handling sequences of musical notes."""

from typing import List, Optional, Sequence, Union, Any, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator

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

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: List[Union[Note, int]]) -> List[Note]:
        """Validate notes in the sequence."""
        validated_notes = []
        for note in v:
            if isinstance(note, int):
                validated_notes.append(Note.from_midi(note))
            elif isinstance(note, Note):
                validated_notes.append(note)
            else:
                raise ValueError(f"Invalid note type: {type(note)}")
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
    ) -> None:
        """Add a note to the sequence."""
        if isinstance(note, Note):
            transposed_note = note.transpose(0)  # Assuming 0 semitones for simplicity
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
        for event in self.events:
            if isinstance(event.note, Note):
                event.note.transpose(semitones)
            elif isinstance(event.note, int):
                # Handle int case appropriately, if needed
                pass
            else:
                raise TypeError("Invalid note type in sequence")


class PatternInterpreter(BaseModel):
    """Base class for pattern interpreters."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    pattern: Sequence[Union[int, str, Note, ScaleDegree, dict[str, Any]]]

    def interpret(self, position: float = 0.0) -> NoteSequence:
        """Interpret the pattern and return a note sequence."""
        raise NotImplementedError


class ScalePatternInterpreter(PatternInterpreter):
    """Interpreter for scale-based patterns."""

    scale: Scale
    octave: int = 4

    def interpret(self, position: float = 0.0) -> NoteSequence:
        """Interpret the pattern and return a note sequence."""
        sequence = NoteSequence(notes=[])  # Initialize with an empty list of notes
        for i, step in enumerate(self.pattern):
            if isinstance(step, (int, str)):
                # Get notes from scale
                notes = self.scale.get_notes()  # Remove octave parameter
                if notes:
                    scale_degree = int(step) % len(notes)
                    note = notes[scale_degree]
                    # Set the octave after getting the note
                    if hasattr(note, "octave"):
                        note.octave = self.octave
                    sequence.add_note(note, position + i)
        return sequence


def create_pattern_interpreter(
    pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]],
    scale: Optional[Scale] = None,
    **kwargs: Optional[Dict[str, Any]]
) -> PatternInterpreter:
    """Create an appropriate pattern interpreter for the given pattern."""
    # Determine which interpreter to create based on the pattern type
    if isinstance(pattern, list) and all(isinstance(p, int) for p in pattern):
        return ScalePatternInterpreter(pattern=pattern, scale=scale, **kwargs)
    # Add additional conditions for other pattern types as needed
    return PatternInterpreter(pattern=pattern, **kwargs)
