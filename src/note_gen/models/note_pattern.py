"""Data structures for musical note patterns."""

from __future__ import annotations
from uuid import uuid4

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, model_validator

from src.note_gen.models.patterns import NotePattern , NotePatternData
from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.note import Note

# Type aliases
DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]
NoteType = Union[Note, ScaleDegree, Chord]


class NotePattern(BaseModel):
    id: str = Field(default_factory=uuid4, alias='id')
    name: str
    notes: Optional[List[Note]]
    pattern_type: str = Field(..., description="Type of pattern")
    description: str
    tags: List[str]
    complexity: float = Field(..., description="Pattern complexity")
    data: Optional[List[int]]
    is_test: Optional[bool] = False
    
    class Config:
        orm_mode = True


class NotePatternResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(..., description="Name of the note pattern")
    notes: Optional[List[Note]] = Field(None, description="List of notes in the pattern")
    pattern_type: Optional[str] = Field(None, description="Type of pattern")
    description: str = Field(..., description="Pattern description")
    tags: List[str] = Field(..., description="Pattern tags")
    complexity: Optional[float] = Field(None, description="Pattern complexity")
    data: Optional[Union[NotePatternData, List[Union[int, List[int]]]]] = Field(default=None, description="Additional pattern data")
    is_test: Optional[bool] = Field(default=None, description="Test flag")