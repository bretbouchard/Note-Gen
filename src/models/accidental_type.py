"""Module for defining accidentals in music theory.

This module provides classes and functions for representing musical accidentals, including sharps, flats, and naturals. It allows for the creation and manipulation of accidentals, enabling various musical applications such as composition and analysis.

AccidentalType Class
---------------------

The `AccidentalType` enumeration defines the different types of accidentals used in music:

- `NATURAL`: Represents a natural accidental, indicating that a note should be played without any alteration.
- `SHARP`: Represents a sharp accidental, indicating that a note should be raised by a half step.
- `FLAT`: Represents a flat accidental, indicating that a note should be lowered by a half step.
- `DOUBLE_SHARP`: Represents a double sharp accidental, indicating that a note should be raised by two half steps.
- `DOUBLE_FLAT`: Represents a double flat accidental, indicating that a note should be lowered by two half steps.

Usage
-----

To use the `AccidentalType` enumeration, reference the desired accidental type as follows:

```python
accidental = AccidentalType.SHARP
print(accidental)
```

This module is designed to be extensible, allowing for the addition of new accidental types and functionalities as needed.

"""
from src.models.note import Note
from src.models.chord import Chord
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AccidentalType(str, Enum):
    """Enum representing different accidental types."""
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

    def get_offset(self) -> int:
        """Get the semitone offset for this accidental."""
        offset_map = {
            AccidentalType.NATURAL: 0,
            AccidentalType.SHARP: 1,
            AccidentalType.FLAT: -1,
            AccidentalType.DOUBLE_SHARP: 2,
            AccidentalType.DOUBLE_FLAT: -2
        }
        return offset_map[self]

    def get_opposite(self) -> 'AccidentalType':
        """Get the opposite accidental (sharp -> flat, etc.)."""
        opposite_map = {
            AccidentalType.NATURAL: AccidentalType.NATURAL,
            AccidentalType.SHARP: AccidentalType.FLAT,
            AccidentalType.FLAT: AccidentalType.SHARP,
            AccidentalType.DOUBLE_SHARP: AccidentalType.DOUBLE_FLAT,
            AccidentalType.DOUBLE_FLAT: AccidentalType.DOUBLE_SHARP
        }
        return opposite_map[self]

    @classmethod
    def from_string(cls, value: str) -> 'AccidentalType':
        """Create an AccidentalType from a string."""
        try:
            return cls(value)
        except ValueError:
            logger.error(f"Invalid accidental: {value}")
            raise ValueError(f"Invalid accidental: {value}")