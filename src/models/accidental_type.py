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

import logging
from pydantic import BaseModel, ConfigDict
from enum import Enum

class AccidentalType(str, Enum, BaseModel):
    """Enum for musical accidentals."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    NATURAL = ""
    SHARP = "#"
    FLAT = "b"
    DOUBLE_SHARP = "##"
    DOUBLE_FLAT = "bb"

    @classmethod
    def combine(cls, acc1: 'AccidentalType', acc2: 'AccidentalType') -> 'AccidentalType':
        """
        Combine two accidentals and return the resulting accidental.

        The combination rules are as follows:
        - Natural + Natural = Natural
        - Natural + Sharp/Flat = Sharp/Flat
        - Sharp + Sharp = Double Sharp
        - Sharp + Flat = Natural
        - Flat + Flat = Double Flat
        - Flat + Sharp = Natural
        - Double Sharp + Sharp = Double Sharp
        - Double Flat + Flat = Double Flat

        Any other combination is considered unexpected and will raise a ValueError.

        Args:
            acc1 (AccidentalType): The first accidental to combine.
            acc2 (AccidentalType): The second accidental to combine.

        Returns:
            AccidentalType: The resulting accidental after combination.

        Raises:
            ValueError: If the combination is unexpected.

        Notes:
            This method uses a simple if-else statement to handle the different combinations.
            It logs each combination at the DEBUG level and raises a ValueError for unexpected combinations.
        """
        logger = logging.getLogger(__name__)
        logger.debug(f"Combining accidentals: {acc1}, {acc2}")
        if acc1 == cls.NATURAL:
            logger.debug(f"Returning {acc2} since {acc1} is natural")
            return acc2
        if acc2 == cls.NATURAL:
            logger.debug(f"Returning {acc1} since {acc2} is natural")
            return acc1
        
        # Handle sharps
        if acc1 == cls.SHARP and acc2 == cls.SHARP:
            logger.debug(f"Combined {acc1} and {acc2} to get {cls.DOUBLE_SHARP}")
            return cls.DOUBLE_SHARP
        if acc1 == cls.SHARP and acc2 == cls.FLAT:
            logger.debug(f"Combined {acc1} and {acc2} to get {cls.NATURAL}")
            return cls.NATURAL
            
        # Handle flats
        if acc1 == cls.FLAT and acc2 == cls.FLAT:
            logger.debug(f"Combined {acc1} and {acc2} to get {cls.DOUBLE_FLAT}")
            return cls.DOUBLE_FLAT
        if acc1 == cls.FLAT and acc2 == cls.SHARP:
            logger.debug(f"Combined {acc1} and {acc2} to get {cls.NATURAL}")
            return cls.NATURAL
        
        # Handle double accidentals
        if acc1 == cls.DOUBLE_SHARP and acc2 == cls.SHARP:
            logger.debug(f"Combined {acc1} and {acc2} to get {cls.DOUBLE_SHARP}")
            return cls.DOUBLE_SHARP
        if acc1 == cls.DOUBLE_FLAT and acc2 == cls.FLAT:
            logger.debug(f"Combined {acc1} and {acc2} to get {cls.DOUBLE_FLAT}")
            return cls.DOUBLE_FLAT
        
        logger.error(f"Unexpected accidental combination: {acc1}, {acc2}")
        raise ValueError(f"Unexpected accidental combination: {acc1}, {acc2}")
