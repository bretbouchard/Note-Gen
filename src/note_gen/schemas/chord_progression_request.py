from pydantic import BaseModel, Field
from typing import List, Optional
from src.note_gen.core.enums import ScaleType

class ChordProgressionRequest(BaseModel):
    """Request model for chord progression creation."""
    name: str
    key: str
    scale_type: ScaleType
    chords: List[str]
    complexity: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class ProgressionGenerationRequest(BaseModel):
    """Request model for chord progression generation."""
    key: str
    scale_type: ScaleType
    complexity: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    length: Optional[int] = Field(default=4, ge=1, le=16)

class ValidationResponse(BaseModel):
    """Response model for validation results."""
    is_valid: bool
    errors: List[str] = []
