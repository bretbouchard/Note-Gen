"""Module for defining musical patterns.

This module provides classes and functions for defining various musical patterns used in compositions. It includes implementations for different types of patterns, such as rhythmic patterns, melodic patterns, and harmonic patterns, allowing for flexible musical composition and manipulation.
"""
from typing import Any, List, Literal, Dict, Union

from pydantic import BaseModel, Field, ConfigDict


DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]

class RhythmNote(BaseModel):
    """A single note in a rhythm pattern."""
    position: float = Field(default=0.0)
    duration: float = Field(default=1.0)
    velocity: float = Field(default=100.0)
    is_rest: bool = Field(default=False)
    accent: str | None = Field(default=None)
    swing_ratio: float | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def validate_velocity(cls, v: float) -> float:
        if not 0 <= v <= 127:
            raise ValueError("Velocity must be between 0 and 127")
        return v

    @classmethod
    def validate_duration(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v

    def get(self, key: str, default: Any | None = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def dict(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(**kwargs)

class RhythmPatternData(BaseModel):
    """Data for a rhythm pattern."""
    notes: List[RhythmNote] = Field(default_factory=list)
    duration: float = Field(default=0.0)
    time_signature: str = Field(default="4/4")
    swing_enabled: bool = Field(default=False)
    swing_ratio: float = Field(default=0.67)
    groove_type: str | None = Field(default=None)
    variation_probability: float = Field(default=0.0)
    humanize_amount: float = Field(default=0.0)
    accent_pattern: list[str] | None = Field(default=None)
    default_duration: float = Field(default=1.0)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def check_notes(cls, v: Union[list[Union[dict, RhythmNote]], Any]) -> list[RhythmNote]:
        if not isinstance(v, list):
            raise ValueError("Notes must be a list")
        return [RhythmNote(**note) if isinstance(note, dict) else note for note in v]

    @classmethod
    def check_duration(cls, v: Union[int, float]) -> float:
        if v < 0:
            raise ValueError("Duration must be non-negative")
        return v

    @classmethod
    def check_time_signature(cls, v: Union[str, Any]) -> str:
        if not isinstance(v, str) or '/' not in v:
            raise ValueError("Invalid time signature format")
        return v

class MusicalPattern(BaseModel):
    """Base class for musical patterns."""
    pattern_data: List[Dict[str, Any]]
    notes: List[RhythmNote] = Field(default_factory=list)
    duration: float = Field(default=0.0)
    time_signature: str = Field(default="4/4")
    swing_enabled: bool = Field(default=False)
    swing_ratio: float = Field(default=0.67)
    groove_type: str | None = Field(default=None)
    variation_probability: float = Field(default=0.0)
    humanize_amount: float = Field(default=0.0)
    accent_pattern: list[str] | None = Field(default=None)
    default_duration: float = Field(default=1.0)

    class Config:
        arbitrary_types_allowed = True

    def generate(self) -> List[Any]:
        """Generate the musical sequence based on the pattern data.

        Returns:
            List[Any]: The generated musical sequence.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @classmethod
    def validate_swing_ratio(cls, v: float | None) -> float | None:
        if v is not None and not 0 <= v <= 1:
            raise ValueError("Swing ratio must be between 0 and 1")
        return v

    @classmethod
    def validate_variation_probability(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Variation probability must be between 0 and 1")
        return v

    @classmethod
    def validate_humanize_amount(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Humanize amount must be between 0 and 1")
        return v

    def _update_duration(self) -> None:
        if self.notes:
            self.duration = max(note.position + note.duration for note in self.notes)

    def apply_swing(self) -> None:
        if not self.swing_enabled:
            return