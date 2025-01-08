from __future__ import annotations
import logging
import sys
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

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

    def __init__(
        self,
        *,
        notes: List[RhythmNote] = [],
        time_signature: str = "4/4",
        swing_enabled: bool = False,
        humanize_amount: float = 0.0,
        swing_ratio: float = 0.67,
        style: Optional[str] = None,
        default_duration: float = 1.0,
    ) -> None:
        super().__init__(
            notes=notes,
            time_signature=time_signature,
            swing_enabled=swing_enabled,
            humanize_amount=humanize_amount,
            swing_ratio=swing_ratio,
            style=style,
            default_duration=default_duration,
        )

    @field_validator("humanize_amount")
    def validate_humanize_amount(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Humanize amount must be non-negative.")
        return value

    @field_validator("swing_ratio")
    def validate_swing_ratio(cls, value: float) -> float:
        if not (0.5 <= value <= 0.75):
            raise ValueError("Swing ratio must be between 0.5 and 0.75.")
        return value

    @field_validator("notes")
    def validate_notes(cls, notes: List[RhythmNote]) -> List[RhythmNote]:
        if not notes:
            raise ValueError("Cannot calculate total duration: no notes present.")
        return notes

    def calculate_total_duration(self) -> None:
        """Calculate the total duration of the rhythm pattern."""
        if not self.notes:
            self.total_duration = 0.0
            logger.debug("No notes found; total duration set to 0.")
            return

        valid_notes = [note for note in self.notes if not note.is_rest]
        if not valid_notes:
            self.total_duration = 0.0
            logger.debug("All notes are rests; total duration set to 0.")
            return

        self.total_duration = max(note.position + note.duration for note in valid_notes)
        logger.debug(f"Calculated total duration: {self.total_duration}")


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
