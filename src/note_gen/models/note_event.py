"""Module for note event models."""

import logging
from typing import Union, Any, Dict
from pydantic import Field, field_validator, ConfigDict

from note_gen.models.note import Note
from note_gen.models.chord import Chord
from note_gen.models.scale_degree import ScaleDegree
from note_gen.models.base import BaseModelWithConfig
from note_gen.core.enums import ValidationLevel
from note_gen.validation.base_validation import ValidationResult
from note_gen.validation.validation_manager import ValidationManager

# Set up logging
logger = logging.getLogger(__name__)


class NoteEvent(BaseModelWithConfig):
    """A musical event with timing information."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        frozen=False,
        json_schema_extra={
            "example": {
                "note": "C4",
                "position": 0.0,
                "duration": 1.0,
                "velocity": 100,
                "channel": 0,
                "is_rest": False
            }
        }
    )

    note: Union[Note, ScaleDegree, Chord]
    position: float = Field(
        default=0.0, 
        ge=0,
        description="Position in beats"
    )
    duration: float = Field(
        default=1.0, 
        gt=0,
        description="Duration in beats"
    )
    velocity: int = Field(
        default=100, 
        ge=0, 
        le=127,
        description="MIDI velocity (0-127)"
    )
    channel: int = Field(
        default=0, 
        ge=0, 
        le=15,
        description="MIDI channel (0-15)"
    )
    is_rest: bool = Field(
        default=False,
        description="Whether this event represents a rest"
    )

    @field_validator('position')
    @classmethod
    def validate_position(cls, value: float) -> float:
        """Validate position with specific error message."""
        if value < 0:
            raise ValueError("Position cannot be negative")
        return value

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, value: float) -> float:
        """Validate duration with specific error message."""
        if value <= 0:
            raise ValueError("Duration must be positive")
        return value

    @field_validator('note')
    @classmethod
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
                # Create a new transposed chord
                self.note = self.note.transpose(semitones)
                logger.debug(f"Successfully transposed chord to: {self.note}")
            else:
                raise TypeError(f"Cannot transpose note of type: {type(self.note)}")
        except ValueError as e:
            logger.error(f"Error during transposition: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary."""
        return {
            "note": self.note.model_dump() if isinstance(self.note, (Note, Chord)) else str(self.note),
            "position": self.position,
            "duration": self.duration,
            "velocity": self.velocity,
            "channel": self.channel,
            "is_rest": self.is_rest
        }

    def __str__(self) -> str:
        return f"NoteEvent(note={self.note}, position={self.position}, duration={self.duration})"

    def validate_event(self, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate note event using validation manager."""
        return ValidationManager.validate_model(
            self.__class__,
            self.model_dump(),
            level
        )

    @classmethod
    def validate_event_data(cls, data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate raw note event data."""
        return ValidationManager.validate_model(cls, data, level)


