"""Models for rhythm patterns."""
from __future__ import annotations

import random
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RhythmNote(BaseModel):
    """A single note in a rhythm pattern."""

    position: float = Field(default=0.0, description="Position in beats")
    duration: float = Field(default=1.0, description="Duration in beats")
    velocity: float = Field(default=100.0, description="Note velocity (0-127)")
    is_rest: bool = Field(default=False, description="Whether this note is a rest")
    accent: str | None = Field(default=None, description="Note accent (staccato, legato, accent)")
    swing_ratio: float | None = Field(default=None, description="Swing ratio for this note (0.5-0.75)")

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)
   
    @field_validator("velocity")
    @classmethod
    def validate_velocity(cls, v: float) -> float:
        """Validate that velocity is between 0 and 127."""
        if not 0 <= float(v) <= 127:
            raise ValueError("Velocity must be between 0 and 127. Invalid value found.")
        return float(v)

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        """Validate that duration is positive."""
        if float(v) <= 0:
            raise ValueError("Duration must be positive. Invalid value found.")
        return float(v)

    def get(self, key: str, default: Any | None = None) -> Any:
        """Provide dictionary-like access to model attributes."""
        try:
            return getattr(self, key, default)
        except AttributeError:
            return default

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style indexing."""
        return getattr(self, key)

    def dict(self, **kwargs: Any) -> dict[str, Any]:
        """Convert to a dictionary representation."""
        return {
            "position": self.position,
            "duration": self.duration,
            "velocity": self.velocity,
            "is_rest": self.is_rest,
            "accent": self.accent,
            "swing_ratio": self.swing_ratio,
        }

class RhythmPatternData(BaseModel):
    """Data for a rhythm pattern."""

    notes: List[RhythmNote] = Field(default_factory=list)
    duration: float = Field(default=0.0, description="Total duration in beats")
    time_signature: str = Field(default="4/4", description="Time signature")
    swing_enabled: bool = Field(default=False, description="Enable swing rhythm")
    swing_ratio: float = Field(default=0.67, description="Global swing ratio (0.5-0.75)")
    groove_type: str | None = Field(default=None, description="Groove type (e.g., 'shuffle', 'straight')")
    variation_probability: float = Field(default=0.0, description="Probability of note variation (0-1)")
    humanize_amount: float = Field(default=0.0, description="Amount of humanization to apply (0-1)")
    accent_pattern: list[str] | None = Field(default=None, description="Pattern of accents to apply")
    default_duration: float = Field(default=1.0, description="Default duration for rhythm patterns")

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)
 

    @field_validator('notes')
    def check_notes(cls, v: List[RhythmNote]) -> List[RhythmNote]:
        """Validate that all items in notes are instances of RhythmNote."""
        if not all(isinstance(note, RhythmNote) for note in v):
            raise ValueError('All items in notes must be instances of RhythmNote. Invalid input found.')
        return v

    @field_validator('duration')
    def check_duration(cls, v: float) -> float:
        """Validate that duration is a non-negative number."""
        if not isinstance(v, (float, int)) or v < 0:
            raise ValueError('Duration must be a non-negative number. Invalid value found.')
        return v

    @field_validator('time_signature')
    def check_time_signature(cls, v: str) -> str:
        """Validate that time_signature is a non-empty string."""
        if not isinstance(v, str) or not v:
            raise ValueError('Time signature must be a non-empty string. Invalid value found.')
        return v

    @field_validator("swing_ratio")
    def validate_swing_ratio(cls, v: float | None) -> float | None:
        """Validate that swing ratio is between 0.5 and 0.75."""
        if v is not None and not 0.5 <= float(v) <= 0.75:
            raise ValueError('Swing ratio must be between 0.5 and 0.75. Invalid value found.')
        return v

    @field_validator("variation_probability")
    def validate_variation_probability(cls, v: float) -> float:
        """Validate that variation probability is between 0 and 1."""
        if not 0 <= float(v) <= 1:
            raise ValueError('Variation probability must be between 0 and 1. Invalid value found.')
        return float(v)

    @field_validator("humanize_amount")
    def validate_humanize_amount(cls, v: float) -> float:
        """Validate that humanize amount is between 0 and 1."""
        if not 0 <= float(v) <= 1:
            raise ValueError('Humanize amount must be between 0 and 1. Invalid value found.')
        return float(v)

    def __init__(self, **data: Any) -> None:
        """Initialize RhythmPatternData with flexible data handling."""
        # Convert any dict notes to RhythmNote objects
        if "notes" in data and isinstance(data["notes"], list):
            data["notes"] = [
                note if isinstance(note, RhythmNote) else RhythmNote(**note)
                for note in data["notes"]
            ]
        super().__init__(**data)
        self._update_duration()

    def _update_duration(self) -> None:
        """Update the total duration based on note positions and durations."""
        if not self.notes:
            self.duration = 0.0
            return
        max_pos = max((note.position + note.duration) for note in self.notes)
        self.duration = max_pos

    def apply_swing(self) -> None:
        """Apply swing to the rhythm pattern."""
        if not self.swing_enabled or not self.notes:
            return

        for note in self.notes:
            # Only apply swing to even-numbered beats
            if int(note.position * 2) % 2 == 0:
                continue

            # Calculate swing offset based on note position
            swing_offset = (self.swing_ratio - 0.5) * 0.5
            note.position += swing_offset

    def humanize(self) -> None:
        """Apply humanization to note timing and velocity."""
        if self.humanize_amount <= 0 or not self.notes:
            return

        for note in self.notes:
            # Randomize timing within humanize_amount
            timing_offset = random.uniform(-self.humanize_amount * 0.1, self.humanize_amount * 0.1)
            note.position = max(0.0, note.position + timing_offset)

            # Randomize velocity within humanize_amount
            velocity_range = int(20 * self.humanize_amount)
            velocity_offset = random.randint(-velocity_range, velocity_range)
            note.velocity = max(0.0, min(127.0, note.velocity + velocity_offset))

    def apply_groove(self) -> None:
        """Apply groove patterns to the rhythm."""
        if not self.groove_type or not self.notes:
            return

        groove_patterns: dict[str, list[float]] = {
            "shuffle": [1.0, 0.7, 0.85, 0.7],
            "straight": [1.0, 0.8, 1.0, 0.8],
            "funk": [1.0, 0.6, 0.9, 0.75]
        }

        if self.groove_type not in groove_patterns:
            return

        pattern = groove_patterns[self.groove_type]
        pattern_length = len(pattern)

        for _i, note in enumerate(self.notes):
            pattern_index = int(note.position * 2) % pattern_length
            note.velocity *= pattern[pattern_index]

    def apply_accents(self) -> None:
        """Apply accent pattern to notes."""
        if not self.accent_pattern or not self.notes:
            return

        accent_values = {
            "accent": 1.2,
            "normal": 1.0,
            "soft": 0.8
        }

        pattern_length = len(self.accent_pattern)
        for i, note in enumerate(self.notes):
            accent = self.accent_pattern[i % pattern_length]
            if accent in accent_values:
                note.velocity *= accent_values[accent]

    def apply_variations(self) -> None:
        """Apply random variations to the rhythm pattern."""
        if self.variation_probability <= 0 or not self.notes:
            return

        for note in self.notes:
            if random.random() < self.variation_probability:
                # Randomly adjust velocity
                velocity_change = random.uniform(-10, 10)
                note.velocity = max(0.0, min(127.0, note.velocity + velocity_change))

class RhythmPattern(BaseModel):
    """Represents a pattern for generating rhythmic notes."""

    name: str = Field(description="Name of the rhythm pattern")
    data: RhythmPatternData = Field(description="Data for the rhythm pattern")
    description: Optional[str] = Field(default="", description="Pattern description")
    tags: list[str] = Field(default_factory=list, description="Pattern tags for categorization")
    complexity: float = Field(default=1.0, description="Pattern complexity score (1-10)")
    style: str | None = Field(default=None, description="Musical style (e.g., 'jazz', 'rock')")
    default_duration: float = Field(default=1.0, description="Default duration for rhythm patterns")
    swing_enabled: bool = Field(default=False, description="Enable swing rhythm")
    swing_ratio: float = Field(default=0.67, description="Global swing ratio (0.5-0.75)")
    groove_type: str | None = Field(default=None, description="Groove type (e.g., 'shuffle', 'straight')")
    variation_probability: float = Field(default=0.0, description="Probability of note variation (0-1)")
    humanize_amount: float = Field(default=0.0, description="Amount of humanization to apply (0-1)")
    accent_pattern: list[str] | None = Field(default=None, description="Pattern of accents to apply")

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('name')
    def check_name(cls, v: str | None) -> str | None:
        """Validate that name is a string."""
        if v is not None and not isinstance(v, str):
            raise ValueError('Name must be a string. Invalid value found.')
        return v

    @field_validator('data')
    def check_data(cls, v: RhythmPatternData | dict[str, Any]) -> RhythmPatternData:
        """Validate that data is a RhythmPatternData object."""
        if not isinstance(v, RhythmPatternData):
            v = RhythmPatternData(**v)
        return v

    def __init__(self, **data: Any) -> None:
            """Initialize RhythmPattern with flexible data handling."""
            # Handle nested data dictionary
            if "data" in data and isinstance(data["data"], dict):
                # Ensure RhythmPatternData is created with correct defaults
                data["data"] = RhythmPatternData(**data["data"])

            # If no data provided, create a default RhythmPatternData
            if "data" not in data:
                data["data"] = RhythmPatternData()

            super().__init__(**data)

    def _get_beat_position(self, position: float) -> float:
        """Get the position within the current beat."""
        return position % self.data.duration

    def _get_beat_number(self, position: float) -> int:
        """Get the beat number for a given position."""
        return int(position // self.data.duration)

    def get_events_at_position(self, position: float) -> List[RhythmNote]:
        """Get all events at a specific position."""
        return [event for event in self.data.notes if event.position == position]

    def get_events_in_beat(self, beat_number: int) -> List[RhythmNote]:
        """Get all events in a given beat."""
        beat_start = beat_number * self.data.duration
        beat_end = (beat_number + 1) * self.data.duration
        return [event for event in self.data.notes if beat_start <= event.position < beat_end]

    def get_events_in_range(self, start_position: float, end_position: float) -> List[RhythmNote]:
        """Get all events within a range of positions."""
        return [event for event in self.data.notes if start_position <= event.position < end_position]
