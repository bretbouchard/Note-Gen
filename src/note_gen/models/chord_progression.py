from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
import re
from .chord import Chord
from .scale_info import ScaleInfo

class ChordProgression(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True
    )
    
    id: Optional[str] = Field(default=None)
    name: str = Field(..., min_length=2)
    key: str = Field(...) # Remove pattern validation since we'll handle it in validator
    scale_type: str = Field(...)
    scale_info: Union[str, ScaleInfo] = Field(...)
    chords: List[Chord] = Field(..., min_length=1, max_length=32)
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    genre: Optional[str] = Field(default=None)

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate and normalize the key format."""
        if not isinstance(v, str):
            raise ValueError("Key must be a string")
            
        v = v.strip()
        # Allow uppercase and lowercase letter names
        key_pattern = r'^[A-Ga-g][#b]?m?$'
        
        if not re.match(key_pattern, v):
            raise ValueError("Invalid key format. Must be A-G with optional # or b and optional m")
        
        # Normalize to uppercase except for 'm' suffix
        base = v[:-1].upper() if v.endswith('m') else v.upper()
        suffix = 'm' if v.endswith('m') else ''
        return base + suffix

    @model_validator(mode='after')
    def validate_scale_info(self) -> 'ChordProgression':
        """Validate scale info matches key and scale type."""
        if isinstance(self.scale_info, ScaleInfo):
            if self.scale_info.key.upper() != self.key.upper():
                raise ValueError("Scale info key must match progression key")
            if self.scale_info.scale_type.value != self.scale_type:
                raise ValueError("Scale info scale type must match progression scale type")
        return self