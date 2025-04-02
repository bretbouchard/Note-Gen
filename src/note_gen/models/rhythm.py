"""Models for rhythm patterns."""
from typing import List, Optional, Tuple, Any

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict
)

class RhythmNote(BaseModel):
    """Model representing a rhythmic note."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    
    position: float = Field(default=0.0, ge=0.0)
    duration: float = Field(default=1.0, gt=0.0)
    velocity: int = Field(default=64, ge=0, le=127)
    accent: bool = Field(default=False)
    groove_offset: float = Field(default=0.0, ge=-1.0, le=1.0)
    tuplet_ratio: Optional[Tuple[int, int]] = Field(default=(1, 1))  # Make Optional and provide default
    swing_ratio: float = Field(default=0.5)
    note: Optional[Any] = None

    def get_actual_duration(self) -> float:
        """Get the actual duration of the note, accounting for tuplets."""
        if not self.tuplet_ratio or self.tuplet_ratio == (1, 1):
            return self.duration
        return self.duration * (self.tuplet_ratio[0] / self.tuplet_ratio[1])

class RhythmPattern(BaseModel):
    """Model for rhythm patterns."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    
    name: str = Field(default="")
    pattern: List[RhythmNote] = Field(default_factory=list)
    time_signature: Tuple[int, int] = Field(default=(4, 4))
    total_duration: float = Field(default=4.0)
    style: str = Field(default="basic")
    description: Optional[str] = None
    swing_enabled: bool = Field(default=False)

    def __str__(self) -> str:
        """Return a string representation of the rhythm pattern."""
        return f"{self.name} ({self.time_signature[0]}/{self.time_signature[1]})"

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
        
        return self

# Update forward references
RhythmNote.model_rebuild()
