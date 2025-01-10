from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing_extensions import Annotated

class RhythmPatternData(BaseModel):
    """Data for a rhythm pattern."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        validate_assignment=True
    )

    notes: List[Any] = Field(default=[])
    duration: Annotated[float, Field(default=0.0)]
    # Use a regex constraint to only allow specific time signatures
    time_signature: Annotated[
        str, 
        Field(default="4/4", regex=r"^(4/4|3/4|2/4|6/8)$")
    ]
    swing_enabled: Annotated[bool, Field(default=False)]
    humanize_amount: Annotated[float, Field(default=0.0)]
    accent_pattern: Annotated[Optional[List[str]], Field(default=None)]
    swing_ratio: Annotated[float, Field(default=0.67)]
    groove_type: Annotated[Optional[str], Field(default=None)]
    variation_probability: Annotated[float, Field(default=0.0, ge=0, le=1)]
    default_duration: Annotated[float, Field(default=1.0)]
    total_duration: float = Field(default=0.0, description="Total duration of the rhythm pattern")

    @field_validator("notes", mode="before")
    def allow_empty_notes(cls, v: List[Any]) -> List[Any]:
        return v

    @field_validator("duration")
    def validate_duration(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Duration must be non-negative")
        return v


    @field_validator("swing_ratio")
    def validate_swing_ratio(cls, v: float) -> float:
        if not (0.5 <= v <= 0.75):
            raise ValueError("Swing ratio must be between 0.5 and 0.75.")
        return v

    @field_validator("humanize_amount")
    def validate_humanize_amount(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Humanize amount must be between 0 and 1. Invalid value found.")
        return v

    @field_validator("accent_pattern")
    def validate_accent_pattern(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and not all(isinstance(acc, str) for acc in v):
            raise ValueError("Accent pattern must be a list of strings")
        return v

    @field_validator("groove_type")
    def validate_groove_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["straight", "swing"]:
            raise ValueError("Groove type must be either 'straight' or 'swing'")
        return v

    @field_validator("variation_probability")
    def validate_variation_probability(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError("Variation probability must be between 0 and 1")
        return v

    @field_validator("notes")
    def validate_notes(cls, value: List[Any]) -> List[Any]:
        if not value:
            raise ValueError("Notes cannot be empty.")
        return value

    @field_validator("default_duration")
    def validate_default_duration(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Default duration must be a positive float.")
        return v

    def recalculate_pattern_duration(self) -> None:
        if self.notes:
            self.total_duration = max(
                note.position + note.duration for note in self.notes
            )
        else:
            self.total_duration = 0.0

    def model_post_init(self, _: None) -> None:
        self.recalculate_pattern_duration()