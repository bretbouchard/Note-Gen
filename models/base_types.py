"""Module for defining basic types used in music theory.

This module provides basic types and utility functions that are commonly used throughout the music theory application. It serves as a foundation for more complex types and structures used in musical analysis and composition.

Base Types
----------

The module includes basic types for notes and intervals, as well as the `Note` class for representing musical notes, including their alterations.

Usage
-----

To create a musical note, instantiate the `Note` class with the desired note name and alterations:

```python
note = Note(note_name='C', accidental=AccidentalType.SHARP)
print(note)
```

This module is designed to be extensible, allowing for the addition of new types and utilities as needed.

Base types for music theory models."""

from __future__ import annotations

import logging
from typing import Optional, Any
from pydantic import BaseModel, Field, ValidationError

from .accidental_type import AccidentalType

class Note(BaseModel):
    """A musical note."""
    note_name: str = Field(description="The note name (A-G)")
    accidental: AccidentalType = Field(
        default=AccidentalType.NATURAL,
        description="The accidental applied to this note"
    )
    midi_number: int = Field(description="The MIDI note number")
    duration: float = Field(default=1.0, description="The duration of the note")
    velocity: Optional[int] = Field(default=None, description="The velocity of the note")
    position: Optional[float] = Field(default=None, description="The position of the note")
    octave_offset: int = Field(default=0, description="The octave offset")
    is_chord_note: bool = Field(default=False, description="Whether this note is part of a chord")
    scale_type: Optional[str] = Field(default="major", description="The scale type")
    key: Optional[str] = Field(default="C", description="The key")

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: Any) -> None:
        logger = logging.getLogger(__name__)
        try:
            logger.info(f"Initializing Note with data: {data}")
            super().__init__(**data)
            # Validate critical fields
            if not self.note_name:
                logger.error("Note name must be provided.")
                raise ValueError("Note name must be provided.")
            if self.midi_number < 0 or self.midi_number > 127:
                logger.error("MIDI number must be between 0 and 127.")
                raise ValueError("MIDI number must be between 0 and 127.")
            logger.debug(f"Note initialized with note_name: {self.note_name}, midi_number: {self.midi_number}")
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise
