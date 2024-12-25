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
from typing import TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    pass


class MusicalBase(BaseModel):
    """Base class for all musical models."""

    class Config:
        arbitrary_types_allowed = True
