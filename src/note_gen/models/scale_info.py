from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .note import Note
from .enums import ScaleType

class ScaleInfo(BaseModel):
    """Information about a musical scale."""
    key: str = Field(..., description="The key of the scale")
    scale_type: ScaleType = Field(default=ScaleType.MAJOR, description="The type of scale")
    
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    def __str__(self) -> str:
        return f"{self.key} {self.scale_type.value}"


