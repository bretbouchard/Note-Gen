"""Models for rhythm patterns."""
from typing import List, Tuple, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from .base import BaseModelWithConfig
from .rhythm_note import RhythmNote
from ..core.enums import ScaleType

class RhythmPattern(BaseModelWithConfig):
    """Model for rhythm patterns."""
    model_config = ConfigDict(
        validate_assignment=True,
        extra='allow'  # Allow extra fields
    )

    name: str = Field(default="", description="Name of the rhythm pattern")
    pattern: List[RhythmNote] = Field(default_factory=list, description="List of rhythm notes")
    time_signature: Tuple[int, int] = Field(default=(4, 4), description="Time signature as tuple (beats, beat_unit)")
    swing_enabled: bool = Field(default=False, description="Whether swing is enabled")
    humanize_enabled: bool = Field(default=False, description="Whether humanization is enabled")
    total_duration: float = Field(default=4.0, description="Total duration in beats")
    style: str = Field(default="basic", description="Style of the rhythm pattern")
    description: Optional[str] = Field(default=None, description="Description of the rhythm pattern")
    scale_type: Optional[ScaleType] = Field(default=None, description="Scale type for the pattern")

    @field_validator('time_signature')
    @classmethod
    def validate_time_signature(cls, v: Tuple[int, int]) -> Tuple[int, int]:
        """Validate time signature."""
        numerator, denominator = v
        valid_denominators = [2, 4, 8, 16]
        if denominator not in valid_denominators:
            raise ValueError(f"Invalid time signature denominator. Must be one of: {valid_denominators}")
        if numerator <= 0:
            raise ValueError("Time signature numerator must be positive")
        return v

    @model_validator(mode='after')
    def validate_pattern(self) -> 'RhythmPattern':
        """Validate the rhythm pattern."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")

        # Check for ordered positions
        positions = [note.position for note in self.pattern]
        if positions != sorted(positions):
            raise ValueError("Pattern notes must be in chronological order")

        # Validate total duration
        if any(note.position + note.duration > self.total_duration for note in self.pattern):
            raise ValueError("Note positions and durations exceed total pattern duration")

        return self

    def __str__(self) -> str:
        """String representation of the rhythm pattern."""
        time_sig_str = f"{self.time_signature[0]}/{self.time_signature[1]}"
        return f"RhythmPattern(name='{self.name}', time_signature={time_sig_str}, notes={len(self.pattern)})"
