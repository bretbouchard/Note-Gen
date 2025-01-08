from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing_extensions import Annotated


class RhythmPatternData(BaseModel):
    """Data for a rhythm pattern."""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    notes: List[Any] = Field(default=[])
    duration: Annotated[float, Field(default=0.0)]
    time_signature: Annotated[str, Field(default="4/4")]
    swing_enabled: Annotated[bool, Field(default=False)]
    humanize_amount: Annotated[float, Field(default=0.0)]
    accent_pattern: Annotated[Optional[List[str]], Field(default=None)]
    swing_ratio: Annotated[float, Field(default=0.67)]
    groove_type: Annotated[Optional[str], Field(default=None)]
    variation_probability: Annotated[float, Field(default=0.0, ge=0, le=1)]
    default_duration: Annotated[float, Field(default=1.0)]
    total_duration: float = Field(
        default=0.0, description="Total duration of the rhythm pattern"
    )

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Duration must be non-negative")
        return v

    @field_validator("time_signature")
    def validate_time_signature(cls, value: str) -> str:
        # Simple validation: check if numerator/denominator are common values
        valid_signatures = {"4/4", "3/4", "2/4", "6/8"}  # Extend as needed
        if value not in valid_signatures:
            raise ValueError("Invalid time signature")
        return value

    @field_validator("swing_ratio")
    @classmethod
    def validate_swing_ratio(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError("Swing ratio must be between 0 and 1")
        return v

    @field_validator("humanize_amount")
    @classmethod
    def validate_humanize_amount(cls, v: float) -> float:
        """Validate that humanize amount is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError(
                "Humanize amount must be between 0 and 1. Invalid value found."
            )
        return v

    @field_validator("swing_enabled")
    @classmethod
    def validate_swing_enabled(cls, v: bool) -> bool:
        return v

    @field_validator("accent_pattern")
    @classmethod
    def validate_accent_pattern(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and not all(isinstance(acc, str) for acc in v):
            raise ValueError("Accent pattern must be a list of strings")
        return v

    @field_validator("groove_type")
    @classmethod
    def validate_groove_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["straight", "swing"]:
            raise ValueError("Groove type must be either 'straight' or 'swing'")
        return v

    @field_validator("variation_probability")
    @classmethod
    def validate_variation_probability(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError("Variation probability must be between 0 and 1")
        return v

    def recalculate_pattern_duration(self) -> None:
        if self.notes:
            self.total_duration = max(
                note.position + note.duration for note in self.notes
            )
        else:
            self.total_duration = 0.0

    def __init__(self, notes: List[Any] = [], **data: Any) -> None:
        if not notes:
            raise ValueError("Notes cannot be empty.")
        print("Initializing RhythmPatternData with:")
        print(f"  notes: {notes}")
        print(f"  duration: {self.duration}")
        print(f"  time_signature: {self.time_signature}")
        print(f"  swing_enabled: {self.swing_enabled}")
        print(f"  humanize_amount: {self.humanize_amount}")
        print(f"  accent_pattern: {self.accent_pattern}")
        print(f"  swing_ratio: {self.swing_ratio}")
        super().__init__(**data)
        if notes is not None:
            self.notes = notes
        self.recalculate_pattern_duration()
