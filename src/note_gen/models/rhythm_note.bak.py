"""RhythmNote model definition."""
from typing import Tuple, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
from pydantic.type_adapter import IncEx

class RhythmNote(BaseModel):
    """A note in a rhythm pattern."""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    position: float = Field(default=0.0, description="Position in beats")
    duration: float = Field(default=1.0, description="Duration in beats")
    velocity: float = Field(default=64.0, description="Velocity (0-127)")
    note: Optional[Note] = Field(default=None, description="Optional note information")
    accent: bool = Field(default=False, description="Whether the note is accented")
    tuplet_ratio: Tuple[int, int] = Field(default=(1, 1), description="Tuplet ratio")
    swing_ratio: float = Field(default=0.5, description="Swing ratio")
    humanize_amount: float = Field(default=0.0, description="Humanization amount")
    groove_offset: float = Field(default=0.0, description="Groove timing offset")

    def get_actual_duration(self) -> float:
        """Calculate actual duration considering tuplets."""
        ratio_num, ratio_den = self.tuplet_ratio
        return self.duration * ratio_num / ratio_den

    def get_velocity_int(self) -> int:
        """Get velocity as an integer value."""
        return int(self.velocity)

    def model_dump(
        self,
        *,
        mode: str = 'python',
        include: Optional[IncEx] = None,
        exclude: Optional[IncEx] = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: Union[bool, Literal['none', 'warn', 'error']] = True,
        context: Optional[Dict[str, Any]] = None,
        serialize_as_any: bool = False
    ) -> Dict[str, Any]:
        """Override model_dump to ensure compatibility with pydantic v2."""
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            context=context,
            serialize_as_any=serialize_as_any
        )
