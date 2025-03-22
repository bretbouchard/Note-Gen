from pydantic import BaseModel, Field, model_validator

class RhythmNote(BaseModel):
    """Represents a rhythm note with its properties."""
    
    model_config = {
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
        "extra": "ignore",
        "frozen": True  # Make instances immutable
    }
    
    position: float = Field(
        0.0,
        description="Position of the note in time",
        ge=0,
        lt=float('inf')
    )
    duration: float = Field(
        1.0,
        description="Duration of the note in beats",
        gt=0,
        lt=float('inf')
    )
    velocity: int = Field(
        64,
        description="Velocity of the note (0-127)",
        ge=0,
        le=127
    )
    accent: bool = Field(
        False,
        description="Whether the note is accented"
    )
    tuplet_ratio: tuple[int, int] = Field(
        (1, 1),
        description="Tuplet ratio (e.g., (3,2) for triplets)"
    )
    groove_offset: float = Field(
        0.0,
        description="Timing offset for groove (-1.0 to 1.0)",
        ge=-1.0,
        le=1.0
    )
    groove_velocity: float = Field(
        1.0,
        description="Velocity multiplier for groove (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    swing_ratio: float = Field(
        0.5,
        description="Swing ratio for the note (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )