from __future__ import annotations
import logging
import sys
import re
from typing import List, Optional, Type, Any
from pydantic import BaseModel, Field, validator, field_validator

# Configure logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RhythmNote(BaseModel):
    """A single note in a rhythm pattern."""

    def __init__(
        self,
        *,
        position: float = 0.0,
        duration: float = 1.0,
        velocity: int = 100,
        is_rest: bool = False,
        accent: Optional[int] = None,
        swing_ratio: Optional[float] = None,
    ) -> None:
        super().__init__(
            position=position,
            duration=duration,
            velocity=velocity,
            is_rest=is_rest,
            accent=accent,
            swing_ratio=swing_ratio,
        )

    position: float = Field(0.0, description="Position in beats")
    duration: float = Field(1.0, description="Duration in beats")
    velocity: int = Field(100, description="Note velocity (0-127)")
    is_rest: bool = Field(False, description="Indicates if the note is a rest")
    accent: Optional[int] = Field(
        None, description="Note accent (e.g., staccato, legato, accent)"
    )
    swing_ratio: Optional[float] = Field(
        None, description="Swing ratio for this note (0.5-0.75)"
    )
    @field_validator("position")
    def validate_position(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Position must be non-negative.")
        return value

    @field_validator("duration")
    def validate_duration(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Duration must be positive.")
        return value

    @field_validator("velocity")
    def validate_velocity(cls, value: int) -> int:
        if not (0 <= value <= 127):
            raise ValueError("Velocity must be between 0 and 127.")
        return value

    @field_validator("swing_ratio")
    def validate_swing_ratio(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not (0.5 <= value <= 0.75):
            raise ValueError("Swing ratio must be between 0.5 and 0.75.")
        return value


class RhythmPatternData(BaseModel):
    """Data for a rhythm pattern."""

    notes: List[RhythmNote] = Field(
        default_factory=list, description="List of rhythmic notes"
    )
    time_signature: str = Field(
        "4/4", description="Time signature in 'numerator/denominator' format"
    )
    swing_enabled: bool = Field(False, description="Indicates if swing is enabled")
    humanize_amount: float = Field(0.0, description="Amount to humanize the pattern")
    swing_ratio: float = Field(0.67, description="Global swing ratio (0.5-0.75)")
    style: Optional[str] = Field(None, description="Musical style (e.g., jazz, rock)")
    default_duration: float = Field(1.0, description="Default note duration")
    total_duration: float = Field(
        0.0, description="Total duration of the rhythm pattern"
    )
    accent_pattern: Optional[List[str]] = Field(None, description="Accent pattern")
    groove_type: Optional[str] = Field(None, description="Groove type")
    variation_probability: float = Field(0.0, description="Variation probability")
    duration: float = Field(1.0, description="Default duration of the notes")

    def __init__(self, *, notes: List[RhythmNote], duration: float = 1.0, **data: Any) -> None:
        if duration < 0:
            raise ValueError("Duration must be non-negative.")
        if not notes:
            raise ValueError("Notes cannot be empty.")
        super().__init__(notes=notes, duration=duration, **data)
        self.calculate_total_duration()

    @field_validator("time_signature", mode="before")
    def validate_time_signature(cls, value: str) -> str:
        valid_signatures = {"4/4", "3/4", "2/4", "6/8"}
        if value not in valid_signatures:
            raise ValueError("Invalid time signature")
        return value

    @field_validator("swing_ratio", mode="before")
    @classmethod
    def validate_swing_ratio(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not (0.5 <= value <= 0.75):
            raise ValueError("Swing ratio must be between 0.5 and 0.75.")
        return value

    @field_validator("humanize_amount", mode="before")
    @classmethod
    def validate_humanize_amount(cls, value: float) -> float:
        if not (0 <= value <= 1):
            raise ValueError("Humanize amount must be between 0 and 1. Invalid value found.")
        return value

    @field_validator("accent_pattern", mode="before")
    @classmethod
    def validate_accent_pattern(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is not None and not all(isinstance(acc, str) for acc in value):
            raise ValueError("Accent pattern must be a list of strings")
        return value

    @field_validator("groove_type", mode="before")
    @classmethod
    def validate_groove_type(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ["straight", "swing"]:
            raise ValueError("Groove type must be either 'straight' or 'swing'")
        return value

    @classmethod
    def validate_notes(cls, value: List[RhythmNote]) -> List[RhythmNote]:
        if not value:
            raise ValueError("Notes cannot be empty.")
        return value

    @classmethod
    def validate_default_duration(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Default duration must be a positive float.")
        return value

    @classmethod
    def validate_variation_probability(cls, value: float) -> float:
        if not (0 <= value <= 1):
            raise ValueError("Variation probability must be between 0 and 1.")
        return value

    @field_validator("duration", mode="before")
    def validate_duration(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Duration must be non-negative.")
        return value

    def calculate_total_duration(self) -> float:
        if not self.notes:
            self.total_duration = 0.0
        else:
            self.total_duration = sum(note.duration for note in self.notes)
        return self.total_duration


class RhythmPattern(BaseModel):
    """Represents a pattern for generating rhythmic notes."""

    name: str
    data: RhythmPatternData
    description: Optional[str] = Field("", description="Pattern description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    complexity: float = Field(1.0, description="Pattern complexity score (1-10)")
    style: Optional[str] = Field(None, description="Musical style (e.g., jazz, rock)")

    def __init__(
        self,
        *,
        name: str,
        data: RhythmPatternData,
        description: Optional[str] = "",
        tags: List[str] = [],
        complexity: float = 1.0,
        style: Optional[str] = None,
    ) -> None:
        if not isinstance(data, RhythmPatternData):
            raise TypeError("data must be an instance of RhythmPatternData")
        super().__init__(
            name=name,
            data=data,
            description=description,
            tags=tags,
            complexity=complexity,
            style=style,
        )

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        return value

    @field_validator("data")
    def validate_data(cls, data: RhythmPatternData) -> RhythmPatternData:
        if not isinstance(data, RhythmPatternData):
            raise TypeError("Data must be a RhythmPatternData object.")
        if not data.notes:
            raise ValueError("RhythmPatternData must contain at least one note.")
        return data

    def get_events_in_range(
        self, start_position: float, end_position: float
    ) -> List[RhythmNote]:
        """Get all notes within a specified range of positions."""
        return [
            note
            for note in self.data.notes
            if note.position < end_position
            and (note.position + note.duration) > start_position
        ]

    def get_pattern_duration(self) -> float:
        """Recalculate and return the total duration of the rhythm pattern."""
        self.data.calculate_total_duration()
        return self.data.total_duration
