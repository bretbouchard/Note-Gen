from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from src.note_gen.core.constants import DEFAULTS
from src.note_gen.core.enums import PatternType, ScaleType

class PatternRequest(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    pattern_type: PatternType = Field(default=PatternType.MELODIC)
    root_note: str = Field(default=DEFAULTS["key"])
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    octave: int = Field(default=DEFAULTS["octave"])
    duration: float = Field(default=DEFAULTS["duration"])
    time_signature: tuple[int, int] = Field(default=(4, 4))
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if the request is valid."""
        return all([
            self.root_note,
            self.scale_type,
            isinstance(self.octave, int),
            isinstance(self.duration, (int, float)),
            len(self.time_signature) == 2
        ])
