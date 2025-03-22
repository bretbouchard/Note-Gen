from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ValidationError
)
from typing import List, Union, Dict, Any, Tuple, Optional, Self

class RhythmNote(BaseModel):
    position: float = Field(ge=0.0)
    duration: float = Field(gt=0.0)
    velocity: int = Field(default=64, ge=0, le=127)
    accent: bool = False
    tuplet_ratio: Tuple[int, int] = (1, 1)
    groove_offset: float = 0.0
    groove_velocity: float = 1.0

    @field_validator('position')
    @classmethod
    def validate_position(cls, v: float) -> float:
        if v < 0.0:
            raise ValueError("Position must be non-negative")
        return v

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v: float) -> float:
        if v <= 0.0:
            raise ValueError("Duration must be positive")
        return v

    @field_validator('velocity')
    @classmethod
    def validate_velocity(cls, v: int) -> int:
        if not (0 <= v <= 127):
            raise ValueError("Velocity must be between 0 and 127")
        return v

    @field_validator('tuplet_ratio')
    @classmethod
    def validate_tuplet_ratio(cls, v: Tuple[int, int]) -> Tuple[int, int]:
        """Validate tuplet ratio."""
        if not isinstance(v, tuple) or len(v) != 2:
            raise ValueError("Tuplet ratio must be a tuple of two integers")
        
        numerator, denominator = v
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise ValueError("Tuplet ratio values must be integers")
        
        if numerator <= 0 or denominator <= 0:
            raise ValueError("Tuplet ratio values must be positive")
        
        return v

    @field_validator('groove_offset')
    @classmethod
    def validate_groove_offset(cls, v: float) -> float:
        if v < -1.0 or v > 1.0:
            raise ValueError("Groove offset must be between -1.0 and 1.0")
        return v

    @field_validator('groove_velocity')
    @classmethod
    def validate_groove_velocity(cls, v: float) -> float:
        if v < 0.0 or v > 2.0:
            raise ValueError("Groove velocity must be between 0.0 and 2.0")
        return v

    def get_actual_position(self) -> float:
        """Get the actual position after applying groove offset."""
        return self.position + self.groove_offset

    def get_actual_velocity(self) -> int:
        """Get the actual velocity after applying groove and accent."""
        velocity = self.velocity * self.groove_velocity
        if self.accent:
            velocity = min(int(velocity * 1.5), 127)
        return int(velocity)

    def get_actual_duration(self) -> float:
        """Get the actual duration of the note, accounting for tuplet ratio."""
        numerator, denominator = self.tuplet_ratio
        return self.duration * (numerator / denominator)

    def get_grooved_position(self) -> float:
        """Get the position of the note after applying groove offset."""
        return self.position + self.groove_offset

    def get_grooved_velocity(self) -> float:
        """Get the velocity of the note after applying groove velocity."""
        return self.velocity * self.groove_velocity

class RhythmPattern(BaseModel):
    name: str
    pattern: List[RhythmNote]
    time_signature: str
    description: str = ""
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    data: Dict[str, Any] = {}
    groove_template: Optional[Dict[str, List[float]]] = None
    style: str = Field(default="", description="Pattern style")

    @field_validator('pattern', mode='before')
    @classmethod
    def validate_pattern(cls, v: List[Union[Dict[str, Any], RhythmNote]]) -> List[RhythmNote]:
        """Validate pattern."""
        if not v:
            raise ValueError("Pattern cannot be empty")
        
        if isinstance(v, list):
            return [RhythmNote(**item) if isinstance(item, dict) else item for item in v]
        
        raise ValueError(f"Invalid pattern: {v}. Must be a list")

    @field_validator('time_signature')
    @classmethod
    def validate_time_signature(cls, v: str) -> str:
        """Validate time signature format."""
        if not isinstance(v, str):
            raise ValueError("Time signature must be a string")
        
        try:
            numerator, denominator = map(int, v.split('/'))
            if denominator not in [2, 4, 8, 16]:
                raise ValueError("Denominator must be 2, 4, 8, or 16")
            if numerator not in [2, 3, 4, 6, 9, 12]:
                raise ValueError("Numerator must be 2, 3, 4, 6, 9, or 12 for simple and compound meters")
        except (ValueError, TypeError):
            raise ValueError("Time signature must be in the format 'numerator/denominator'")
        
        return v

    @field_validator('complexity')
    @classmethod
    def validate_complexity(cls, v: float) -> float:
        """Validate complexity is between 0.0 and 1.0."""
        if v < 0.0 or v > 1.0:
            raise ValueError("Complexity must be between 0.0 and 1.0")
        return v

    def validate_pattern_duration(self) -> None:
        """Validate that the pattern duration matches the time signature."""
        try:
            numerator, denominator = map(int, self.time_signature.split('/'))
            total_beats = numerator / denominator
            pattern_duration = sum(note.get_actual_duration() for note in self.pattern)
            
            if abs(pattern_duration - total_beats) > 1e-6:
                raise ValueError(f"Pattern duration {pattern_duration} does not match time signature {self.time_signature}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid time signature: {self.time_signature}") from e

    def validate_compound_meter_accents(self) -> None:
        """Validate accents in compound meters."""
        if not self.pattern:
            return

        try:
            numerator, denominator = map(int, self.time_signature.split('/'))
            if denominator == 8 and numerator in [6, 9, 12]:  # Compound meter
                for i, note in enumerate(self.pattern):
                    if i % 3 == 0 and not note.accent:  # First note of each group should be accented
                        raise ValueError("First note of each group in compound meter should be accented")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid time signature: {self.time_signature}") from e

    def apply_groove_template(self, groove_template: Dict[str, List[float]]) -> None:
        """Apply a groove template to the pattern."""
        if not self.pattern:
            return

        if not groove_template:
            return

        # Apply groove offset and velocity from template
        for i, note in enumerate(self.pattern):
            if i < len(groove_template.get('offsets', [])):
                note.groove_offset = groove_template['offsets'][i]
            if i < len(groove_template.get('velocities', [])):
                note.groove_velocity = groove_template['velocities'][i]
