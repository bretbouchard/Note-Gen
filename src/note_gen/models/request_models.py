"""Request models for the API endpoints."""
from typing import Optional, Tuple
from pydantic import Field, ConfigDict
from note_gen.core.constants import DEFAULTS
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.base import BaseModelWithConfig

class GenerateSequenceRequest(BaseModelWithConfig):
    """Request model for sequence generation."""
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        extra='forbid'
    )

    note_pattern_name: str = Field(
        ...,  # This means the field is required
        description="Name of the note pattern to use"
    )
    rhythm_pattern_name: str = Field(
        ...,  # This means the field is required
        description="Name of the rhythm pattern to use"
    )
    progression_name: str = Field(
        ...,  # This means the field is required
        description="Name of the chord progression to use"
    )
    scale_info: ScaleInfo = Field(
        ...,  # Required
        description="Scale information for the sequence"
    )
    time_signature: Tuple[int, int] = Field(
        default=DEFAULTS["time_signature"],
        description="Time signature as (numerator, denominator)"
    )
    tempo: int = Field(
        default=DEFAULTS["bpm"],
        description="Tempo in beats per minute"
    )
    key: str = Field(
        default=DEFAULTS["key"],
        description="Musical key (e.g., 'C4', 'F#4')"
    )
    duration: Optional[float] = Field(
        default=DEFAULTS["duration"],
        description="Duration in beats"
    )

class GenerateRequest(BaseModelWithConfig):
    """Request model for generation endpoints."""
    model_config = ConfigDict(validate_assignment=True)
    # ... rest of the class implementation

class GenerateResponse(BaseModelWithConfig):
    """Response model for generation endpoints."""
    model_config = ConfigDict(validate_assignment=True)
    # ... rest of the class implementation

class ErrorModel(BaseModelWithConfig):
    """Error response model."""
    model_config = ConfigDict(validate_assignment=True)
    # ... rest of the class implementation

class StatusResponse(BaseModelWithConfig):
    """Status response model."""
    model_config = ConfigDict(validate_assignment=True)
    # ... rest of the class implementation
