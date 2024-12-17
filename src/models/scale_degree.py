"""
Module for handling scale degrees.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import logging

from .note import Note

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScaleDegree(BaseModel):
    """A scale degree in a musical scale."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    degree: int = Field(..., description="The degree of the scale (1-7)")
    scale: Optional[str] = None
    note: Optional[Note] = None
    octave: int = Field(default=4, description="Octave number")
    is_flattened: bool = Field(default=False, description="Indicates if the note is flattened")
    value: Optional[int] = Field(default=None, description="The value of the scale degree, if applicable")

    @field_validator('degree')
    @classmethod
    def validate_degree(cls, v: int) -> int:
        if not 1 <= v <= 7:
            logger.error(f"Invalid scale degree: {v}. Must be between 1 and 7.")
            raise ValueError("Degree must be between 1 and 7")
        return v

    @field_validator('octave')
    @classmethod
    def validate_octave(cls, v: int) -> int:
        if not -2 <= v <= 8:
            logger.error(f"Invalid octave: {v}. Must be between -2 and 8.")
            raise ValueError("Octave must be between -2 and 8")
        return v

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation of the ScaleDegree object."""
        logger.debug("Converting ScaleDegree to dictionary representation.")
        d = super().model_dump(**kwargs)
        logger.info("ScaleDegree converted to dictionary successfully.")
        return d

    def to_note(self) -> Note:
        """Convert this scale degree to a Note object."""
        logger.debug("Converting ScaleDegree to Note object.")
        if self.note is None:
            logger.critical("Note not set for scale degree")
            raise ValueError("Note not set for scale degree")
        if self.is_flattened:
            # Create a new flattened note
            flattened = self.note.transpose(-1)
            # If the original note used sharps, convert to flats
            if self.note.accidental == "#":
                next_letter = chr((ord(flattened.name) - ord('A') + 1) % 7 + ord('A'))
                logger.info(f"Converted note to flattened: {next_letter}")
                return Note(
                    name=next_letter,
                    accidental="b",
                    octave=flattened.octave
                )
        logger.info(f"Returning note: {self.note}")
        return self.note
