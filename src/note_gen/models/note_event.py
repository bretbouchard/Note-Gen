"""Module for note event models."""

import logging
from pydantic import BaseModel, Field, ConfigDict, field_validator , model_validator
from typing import Union

from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_degree import ScaleDegree

# Set up logging
logger = logging.getLogger(__name__)


class NoteEvent(BaseModel):
    """Represents a musical note event with timing and performance information."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    note: Union[Note, ScaleDegree, Chord] = Field(
        ..., description="The note associated with the event"
    )
    position: float = Field(default=0.0, description="Position of the note event")
    duration: float = Field(default=1.0, description="Duration of the note event")
    velocity: int = Field(default=100, description="Velocity of the note event")
    channel: int = Field(default=0)
    is_rest: bool = Field(default=False)

    @field_validator("position")
    def validate_position(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Position cannot be negative.")
        return value

    @field_validator("duration")
    def validate_duration(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Duration must be positive.")
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

    @model_validator(mode="after")
    def validate_velocity(self) -> "NoteEvent":
        if not (0 <= self.velocity <= 127):
            raise ValueError("MIDI velocity must be between 0 and 127.")
        return self

    def __str__(self) -> str:
        return f"NoteEvent(note={self.note}, position={self.position}, duration={self.duration})"
