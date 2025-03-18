from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class RhythmPattern(BaseModel):
    pattern: str = Field(..., pattern=r'^-?\d+(\s+-?\d+)*$')
    
    @field_validator('pattern')
    def validate_pattern(cls, v: str) -> str:
        # Add your pattern validation logic here
        return v