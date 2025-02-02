"""Module for note event models."""

import logging
from pydantic import BaseModel, Field, ConfigDict, field_validator, validator, root_validator
from typing import Union, Any, Dict, Optional

from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_degree import ScaleDegree

# Set up logging
logger = logging.getLogger(__name__)


class NoteEvent(BaseModel):
    """A musical event with timing information."""
    note: Union[Note, ScaleDegree, Chord]
    position: float = 0.0
    duration: float = 1.0
    velocity: int = Field(default=100, ge=0, le=127)
    channel: int = 0
    is_rest: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        validate_assignment=True,
        error_messages={
            'velocity': {
                'ge': 'MIDI velocity must be between 0 and 127.',
                'le': 'MIDI velocity must be between 0 and 127.'
            }
        }
    )

    @field_validator('note')
    @classmethod
    def validate_note(cls, value: Any) -> Union[Note, ScaleDegree, Chord]:
        """Validate that note is of correct type."""
        if not isinstance(value, (Note, ScaleDegree, Chord)):
            raise ValueError("Note must be a Note, ScaleDegree, or Chord instance")
        return value

    @field_validator('position')
    @classmethod
    def validate_position(cls, value: float) -> float:
        """Validate position is non-negative."""
        if value < 0:
            raise ValueError("Position cannot be negative.")
        return value

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, value: float) -> float:
        """Validate duration is positive."""
        if value <= 0:
            raise ValueError("Duration must be positive.")
        return value

    @field_validator('velocity')
    @classmethod
    def validate_velocity(cls, value: int) -> int:
        """Validate velocity is within MIDI range."""
        if not (0 <= value <= 127):
            raise ValueError("MIDI velocity must be between 0 and 127.")
        return value

    @field_validator('channel')
    @classmethod
    def validate_channel(cls, value: int) -> int:
        """Validate channel is within MIDI range."""
        if not (0 <= value <= 15):
            raise ValueError("Channel must be between 0 and 15")
        return value

    @property
    def end_position(self) -> float:
        """Get the end position of the note event."""
        return self.position + self.duration

    def overlaps(self, other: "NoteEvent") -> bool:
        """Check if this note event overlaps with another."""
        return self.position < other.end_position and other.position < self.end_position

    def transpose(self, semitones: int) -> None:
        """Transpose the note by the given number of semitones."""
        logger.debug(f"Transposing NoteEvent with MIDI: {self.note} by {semitones} semitones.")
        try:
            if isinstance(self.note, Note):
                transposed_note = self.note.transpose(semitones)
                if transposed_note:
                    self.note = transposed_note
                    logger.debug(f"Successfully transposed note to: {self.note}")
            elif isinstance(self.note, Chord):
                # Transpose each note in the chord
                transposed_root = self.note.root.transpose(semitones)
                if transposed_root:
                    self.note.root = transposed_root
                    self.note.notes = [note.transpose(semitones) for note in self.note.notes]
                    logger.debug(f"Successfully transposed chord to: {self.note}")
            else:
                raise TypeError(f"Cannot transpose note of type: {type(self.note)}")
        except ValueError as e:
            logger.error(f"Error during transposition: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary."""
        return {
            "note": self.note.to_dict() if hasattr(self.note, 'to_dict') else str(self.note),
            "position": self.position,
            "duration": self.duration,
            "velocity": self.velocity,
            "channel": self.channel,
            "is_rest": self.is_rest
        }

    def __str__(self) -> str:
        return f"NoteEvent(note={self.note}, position={self.position}, duration={self.duration})"
