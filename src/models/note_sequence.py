"""Module for handling sequences of musical notes."""
from typing import List, Optional, Sequence, Union, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .note import Note
from .chord import Chord
from .scale_degree import ScaleDegree
from .scale import Scale
from .note_event import NoteEvent

class NoteSequence(BaseModel):
    """A sequence of musical notes with timing information."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    notes: List[int] = Field(default_factory=list)
    events: List[NoteEvent] = Field(default_factory=list)
    duration: float = 0.0

    @field_validator('notes')
    def check_notes(cls, v: List[int]) -> List[int]:
        if not all(isinstance(note, int) for note in v):
            raise ValueError('All notes must be integers.')
        if not all(0 <= note <= 127 for note in v):
            raise ValueError('All notes must be in the MIDI range (0-127).')
        return v

    @field_validator('events')
    def check_events(cls, v: List[NoteEvent]) -> List[NoteEvent]:
        if not all(isinstance(event, NoteEvent) for event in v):
            raise ValueError('All events must be NoteEvent instances.')
        return v

    def add_note(self, note: Union[str, Note, ScaleDegree, Chord], 
                 position: float = 0.0, 
                 duration: float = 1.0,
                 velocity: int = 100) -> None:
        """Add a note to the sequence."""
        event = NoteEvent(
            note=note,
            position=position,
            duration=duration,
            velocity=velocity
        )
        self.events.append(event)
        self._update_duration()  # Ensure duration is updated correctly
    
    def _update_duration(self) -> None:
        if self.events:
            self.duration = max(event.end_position for event in self.events)
    
    def get_notes_at(self, position: float) -> List[NoteEvent]:
        """Get all notes active at the given position."""
        return [event for event in self.events 
                if event.position <= position < event.end_position]
    
    def clear(self) -> None:
        """Clear all notes from the sequence."""
        self.events.clear()
        self.duration = 0.0

    def transpose(self, semitones: int) -> 'NoteSequence':
        """Transpose the note sequence by the given number of semitones."""
        return NoteSequence(notes=[note + semitones for note in self.notes])

NoteSequence.model_rebuild()

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
                    if hasattr(note, 'octave'):
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

NoteSequence.model_rebuild()