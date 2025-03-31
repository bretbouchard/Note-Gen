"""RhythmNote model definition."""
from typing import Dict, Any, Tuple, Optional, Set, Union, Literal, Callable
from pydantic import BaseModel, Field, ConfigDict
from pydantic.main import IncEx

class RhythmNote(BaseModel):
    """Model representing a rhythmic note."""
    position: float = Field(ge=0.0, description="Position in beats from start")
    duration: float = Field(gt=0.0, description="Duration in beats")
    velocity: float = Field(default=64.0, ge=0.0, le=127.0, description="MIDI velocity")
    accent: bool = Field(default=False, description="Whether the note is accented")
    tuplet_ratio: Tuple[int, int] = Field(default=(1, 1), description="Tuplet ratio (numerator, denominator)")
    swing_ratio: float = Field(default=0.5, ge=0.0, le=1.0, description="Swing ratio for this note")
    humanize_amount: float = Field(default=0.0, ge=0.0, le=1.0, description="Humanization amount")
    groove_offset: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Timing offset for groove patterns (-1.0 to 1.0)"
    )

    model_config = ConfigDict(
        extra='allow',
        validate_assignment=True
    )

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
