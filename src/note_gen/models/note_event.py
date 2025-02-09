"""Module for note event models."""

import logging
from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Union, Any, Dict, Optional

from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_degree import ScaleDegree

# Set up logging
logger = logging.getLogger(__name__)


class NoteEvent(BaseModel):
    """A musical event with timing information."""
    note: Union[Note, ScaleDegree, Chord]
    position: float = Field(default=0.0, ge=0)
    duration: float = Field(default=1.0, gt=0)
    velocity: int = Field(default=100, ge=0, le=127)
    channel: int = Field(default=0, ge=0, le=15)
    is_rest: bool = Field(default=False)

    @field_validator('note')
    def validate_note(cls, value: Any) -> Union[Note, ScaleDegree, Chord]:
        """Validate that note is of correct type."""
        if not isinstance(value, (Note, ScaleDegree, Chord)):
            raise ValueError("Note must be a Note, ScaleDegree, or Chord instance")
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

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
