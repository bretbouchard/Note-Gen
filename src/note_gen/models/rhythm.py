"""Models for rhythm patterns."""
from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator
from .base import BaseModelWithConfig
from .note import Note
from ..core.enums import ScaleType, PatternType  # Add PatternType import

class RhythmNote(BaseModelWithConfig):
    """Model for a rhythm note."""
    note: Optional[Note] = Field(default=None, description="The musical note")
    position: float = Field(default=0.0, ge=0.0, description="Position in beats from start")
    duration: float = Field(default=1.0, gt=0.0, description="Duration in beats")
    velocity: float = Field(default=64.0, ge=0.0, le=127.0, description="MIDI velocity")
    accent: bool = Field(default=False, description="Whether the note is accented")
    tuplet_ratio: Tuple[int, int] = Field(default=(1, 1), description="Tuplet ratio")
    swing_ratio: float = Field(default=0.5, ge=0.0, le=1.0, description="Swing ratio")
    humanize_amount: float = Field(default=0.0, ge=0.0, le=1.0, description="Humanization")
    groove_offset: float = Field(default=0.0, ge=-1.0, le=1.0, description="Groove offset")

    def get_actual_duration(self) -> float:
        """Get the actual duration considering tuplet ratio."""
        numerator, denominator = self.tuplet_ratio
        return self.duration * (numerator / denominator)

    def get_velocity_int(self) -> int:
        """Get the note velocity as integer."""
        return int(self.velocity)

class RhythmPattern(BaseModel):
    """Model for rhythm patterns."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
        validate_assignment=True
    )

    id: str = Field(default="")
    name: str = Field(default="")
    pattern: List[RhythmNote] = Field(default_factory=list)
    pattern_type: PatternType = Field(default=PatternType.RHYTHMIC)  # Changed from RHYTHM to RHYTHMIC
    time_signature: Tuple[int, int] = Field(default=(4, 4))
    swing_enabled: bool = Field(default=False)
    humanize_enabled: bool = Field(default=False)
    swing_ratio: float = Field(default=0.67)
    humanize_amount: float = Field(default=0.0)
    total_duration: float = Field(default=4.0)
    style: str = Field(default="basic")
    description: Optional[str] = Field(default=None)
    scale_type: Optional[ScaleType] = Field(default=None)

    def __str__(self) -> str:
        """Return string representation of the rhythm pattern."""
        time_sig = f"{self.time_signature[0]}/{self.time_signature[1]}"
        return f"{self.name} ({time_sig})"

    @model_validator(mode='after')
    def validate_pattern(self) -> 'RhythmPattern':
        """Validate the rhythm pattern."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")
            
        # Validate time signature denominator (must be power of 2)
        if self.time_signature[1] not in [1, 2, 4, 8, 16, 32, 64]:
            raise ValueError("Time signature denominator must be a power of 2")
            
        # Check if notes are ordered by position
        positions = [note.position for note in self.pattern]
        if positions != sorted(positions):
            raise ValueError("Notes must be ordered by position")
            
        # Calculate actual duration
        actual_duration = sum(note.get_actual_duration() for note in self.pattern)
        
        # Update total_duration if not explicitly set
        if self.total_duration == 4.0:  # default value
            object.__setattr__(self, 'total_duration', actual_duration)
        elif abs(actual_duration - self.total_duration) > 0.001:
            raise ValueError(f"Total duration mismatch: expected {self.total_duration}, got {actual_duration}")
            
        return self

    @classmethod
    def from_preset(cls, preset_name: str) -> 'RhythmPattern':
        """Create a rhythm pattern from a preset name."""
        from ..core.constants import RHYTHM_PATTERNS
        if preset_name not in RHYTHM_PATTERNS:
            raise ValueError(f"Unknown preset: {preset_name}")
            
        preset = RHYTHM_PATTERNS[preset_name]
        return cls(
            name=preset_name,
            pattern=[RhythmNote(position=i, duration=1.0) for i in range(len(preset["notes"]))],
            total_duration=preset["total_duration"],
            description=preset.get("description")
        )
