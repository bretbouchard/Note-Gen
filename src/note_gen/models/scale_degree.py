# src/note_gen/models/scale_degree.py

from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, field_validator

class ScaleDegree(BaseModel):
    """A scale degree with a value."""
    value: int

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
        validate_assignment=True
    )

    @field_validator('value')
    @classmethod
    def validate_value(cls, value: int) -> int:
        """Validate that value is between 1 and 7."""
        if not (1 <= value <= 7):
            raise ValueError("Scale degree must be between 1 and 7")
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert the scale degree to a dictionary."""
        return {
            "value": self.value
        }

    def __str__(self) -> str:
        return f"ScaleDegree({self.value})"