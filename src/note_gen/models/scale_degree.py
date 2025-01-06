# src/note_gen/models/scale_degree.py

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
import logging

from src.note_gen.models.musical_elements import Note

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScaleDegree(BaseModel):
    """Represents a degree in a musical scale."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    degree: int
    note: Note
    
    @field_validator("degree")
    def validate_degree(cls, value: int) -> int:
        if value < 1 or value > 7:
            raise ValueError("Degree must be between 1 and 7.")
        return value

    def __str__(self) -> str:
        return f"ScaleDegree(degree={self.degree}, note={self.note})"

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation of the ScaleDegree object."""
        logger.debug("Converting ScaleDegree to dictionary representation.")
        d = super().model_dump(**kwargs)
        logger.info("ScaleDegree converted to dictionary successfully.")
        return d

    def to_note(self) -> Note:
        """Convert this scale degree to a Note object."""
        logger.debug("Converting ScaleDegree to Note object.")
        logger.info(f"Returning note: {self.note}")
        return self.note