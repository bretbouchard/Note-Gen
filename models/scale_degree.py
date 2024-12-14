"""Module for handling scale degrees."""
from __future__ import annotations

from typing import Any, Dict, Optional, AbstractSet, Mapping
from pydantic import BaseModel, Field

from .note import Note

class ScaleDegree(BaseModel):
    """A scale degree in a musical scale."""
    degree: int
    scale: Optional[str] = None
    note: Optional[Note] = None
    octave: int = Field(default=4)
    is_flattened: bool = Field(default=False)

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'degree': self.degree,
            'scale': self.scale,
            'note': self.note.model_dump() if self.note else None,
            'octave': self.octave,
            'is_flattened': self.is_flattened
        }

    def to_note(self) -> Note:
        """Convert to a Note object."""
        if self.note is None:
            raise ValueError("Note not set for scale degree")
        if self.is_flattened:
            # Create a new flattened note
            flattened = self.note.transpose(-1)
            # If the original note used sharps, convert to flats
            if self.note.accidental == "#":
                next_letter = chr((ord(flattened.name) - ord('A') + 1) % 7 + ord('A'))
                return Note(
                    name=next_letter,
                    accidental="b",
                    octave=flattened.octave
                )
            return flattened
        return self.note

    def copy(self, *, include: AbstractSet[int] | AbstractSet[str] | Mapping[int, Any] | Mapping[str, Any] | None = None,
             exclude: AbstractSet[int] | AbstractSet[str] | Mapping[int, Any] | Mapping[str, Any] | None = None,
             update: dict[str, Any] | None = None,
             deep: bool = False) -> 'ScaleDegree':
        return super().copy(include=include, exclude=exclude, update=update, deep=deep)

    def __str__(self) -> str:
        """String representation of the scale degree."""
        prefix = "b" if self.is_flattened else ""
        return f"{prefix}{self.degree} ({self.note})"

    def transpose(self, semitones: int) -> Note:
        """Transpose the note by the given number of semitones."""
        return self.note.transpose(semitones)
