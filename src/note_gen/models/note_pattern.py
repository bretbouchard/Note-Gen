"""Data structures for musical note patterns."""

from __future__ import annotations

from typing import Any, Literal, Optional, Union, List, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_degree import ScaleDegree


# Type aliases
DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]
NoteType = Union[Note, ScaleDegree, Chord]


class NotePattern(BaseModel):
    """A pattern of musical notes."""
    name: str
    data: List[int]
    notes: List[Note] = Field(default_factory=list)
    description: str = ""
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: List[Note]) -> List[Note]:
        """Validate notes list."""
        if not all(isinstance(note, Note) for note in v):
            raise ValueError("All items in notes must be instances of Note")
        return v

    @property
    def total_duration(self) -> float:
        """Calculate total duration of the pattern."""
        return sum(note.duration for note in self.notes)

    def get_notes(self) -> List[Note]:
        """Get the list of notes in the pattern."""
        return self.notes

    def __str__(self) -> str:
        return f"NotePattern(name={self.name}, data={self.data})"
