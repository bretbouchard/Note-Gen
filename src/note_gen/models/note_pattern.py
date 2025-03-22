from __future__ import annotations

import json
import os
from typing import List, Dict, Optional, Any, Union, Literal, TYPE_CHECKING, cast, Sequence

from pydantic import BaseModel, Field, field_validator, model_validator

if TYPE_CHECKING:
    from src.note_gen.models.note import Note

class NotePatternData(BaseModel):
    """
    Data representing a note pattern.
    A note pattern is a sequence of intervals or notes that can be used to generate a chord progression.
    """
    intervals: Optional[List[int]] = Field(None, description="List of interval values (semitones)")
    notes: Optional[List['Note']] = Field(None, description="List of note objects")
    use_scale_mode: bool = Field(True, description="Whether to use scale mode for generation")
    use_chord_tones: bool = Field(True, description="Whether to use chord tones for generation")
    direction: str = Field("up", description="Direction of the pattern (up, down, or random)")
    restart_on_chord: bool = Field(True, description="Whether to restart the pattern on each chord")
    octave_range: List[int] = Field(default_factory=lambda: [3, 5], description="Range of octaves to use")
    default_duration: float = Field(1.0, description="Default duration for generated notes")
    arpeggio_mode: str = Field("standard", description="Arpeggio mode (standard, inversions, etc.)")

    @model_validator(mode='after')
    def validate_at_least_one_present(self) -> 'NotePatternData':
        """Ensure that at least one of intervals or notes is provided."""
        if self.intervals is None and self.notes is None:
            raise ValueError("At least one of 'intervals' or 'notes' must be provided")
        return self

class NotePattern(BaseModel):
    """
    Model representing a pattern of notes that can be used to generate a chord progression.
    """
    name: str = Field(..., description="Name of the note pattern")
    data: NotePatternData = Field(..., description="Note pattern data")
    description: str = Field("", description="Description of the note pattern")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the pattern")
    complexity: float = Field(0.5, description="Complexity of the pattern (0.0 - 1.0)")
    intervals: Optional[List[int]] = Field(None, description="Legacy field for compatibility")

    @field_validator('complexity')
    @classmethod
    def validate_complexity(cls, v: float) -> float:
        """Validate complexity to ensure it's between 0.0 and 1.0."""
        if v < 0.0 or v > 1.0:
            raise ValueError(f"Complexity must be between 0.0 and 1.0, got {v}")
        return v

    @model_validator(mode='after')
    def sync_intervals(self) -> 'NotePattern':
        """Sync intervals from data if not provided directly."""
        if self.intervals is None and self.data and self.data.intervals:
            self.intervals = self.data.intervals
        elif self.intervals and self.data and self.data.intervals is None:
            self.data.intervals = self.intervals
        return self

    def validate_all(self) -> None:
        """Validate all attributes of the NotePattern instance."""
        if not self.data:
            raise ValueError("NotePattern must have valid data.")
        # Additional validations can be added here as needed
