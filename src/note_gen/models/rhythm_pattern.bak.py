from pydantic import BaseModel, Field, field_validator
from typing import List, Union
from .rhythm_note import RhythmNote
from .patterns import RhythmPatternData

class RhythmPattern(BaseModel):
    name: str
    data: RhythmPatternData
    description: str
    tags: List[str]
    complexity: float
    style: str
    pattern: Union[str, List[float]] = Field(
        ...,
        description="Pattern can be either a string or list of floats"
    )
    
    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: Union[str, List[float]]) -> Union[str, List[float]]:
        """Validate that the pattern is not empty."""
        if isinstance(v, str) and not v:
            raise ValueError("Pattern string cannot be empty")
        if isinstance(v, list) and not v:
            raise ValueError("Pattern list cannot be empty")
        return v
