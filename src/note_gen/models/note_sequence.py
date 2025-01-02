"""Module for handling sequences of musical notes."""

from typing import List, Optional, Sequence, Union, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.note_gen.models.musical_elements import Note, Chord
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
    def check_events(cls, value) -> List[NoteEvent]:
        if not all(isinstance(event, NoteEvent) for event in value):
            raise ValueError("All events must be NoteEvent instances.")
        return value

    def add_note(
        self,
        note: Union[str, Note, ScaleDegree, Chord, int],
        position: float = 0.0,
        duration: float = 1.0,
        velocity: int = 100,
    ) -> None:
        """Add a note to the sequence."""
        if isinstance(note, int):
            note = Note.from_midi(note)
        event = NoteEvent(
            note=note, position=position, duration=duration, velocity=velocity
        )
        self.events.append(event)
        self._update_duration()  # Ensure duration is updated correctly

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

    def transpose(self, semitones: int) -> "NoteSequence":
        """Transpose the note sequence by the given number of semitones."""
        transposed_notes = [note.transpose(semitones) for note in self.notes]
        transposed_events = [
            NoteEvent(
                note=event.note.transpose(semitones),
                position=event.position,
                duration=event.duration,
                velocity=event.velocity,
            )
            for event in self.events
        ]
        return NoteSequence(
            notes=transposed_notes, events=transposed_events, duration=self.duration
        )


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
    pattern: Sequence[Union[int, str, Note, ScaleDegree, dict[str, Any]]],
    scale: Optional[Scale] = None,
    **kwargs: Any
) -> PatternInterpreter:
    """Create an appropriate pattern interpreter for the given pattern."""
    if scale is not None:
        return ScalePatternInterpreter(pattern=pattern, scale=scale, **kwargs)
    return PatternInterpreter(pattern=pattern)
