"""Data structures for musical note patterns."""

from __future__ import annotations

from typing import Literal, Union, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
import uuid

from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_degree import ScaleDegree


# Type aliases
DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]
NoteType = Union[Note, ScaleDegree, Chord]


class NotePattern(BaseModel):
    """A pattern of musical notes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    data: List[Union[int, List[int]]] = Field(...)
    notes: List[Note] = Field(default_factory=list)
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    is_test: bool = Field(default=False)

    class ConfigDict:
        schema_extra = {
            'example': {
                'name': 'Simple Triad',
                'data': [0, 2, 4]
            }
        }
        arbitrary_types_allowed = True

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: List[Note]) -> List[Note]:
        # Ensure all items in the list are instances of Note
        if not all(isinstance(note, Note) for note in v):
            raise ValueError(f"Invalid note type: {v}")
        return v

    @field_validator("data", mode="before")
    def validate_data(cls, value: List[Union[int, List[int]]]) -> List[Union[int, List[int]]]:
        if not value or (isinstance(value, list) and not all(isinstance(item, int) or isinstance(item, list) for item in value)):
            raise ValueError("Data must be a non-empty list of integers or nested lists")
        return value

    @property
    def total_duration(self) -> float:
        """Calculate the total duration of the pattern."""
        return sum(note.duration for note in self.notes)

    def get_notes(self) -> List[Note]:
        """Get the list of notes in the pattern."""
        return self.notes

    def get_duration(self) -> float:
        """Get the total duration of the notes in the pattern."""
        return sum(note.duration for note in self.notes)

    def __str__(self) -> str:
        return f"NotePattern(name={self.name}, data={self.data})"