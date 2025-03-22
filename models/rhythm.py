from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ValidationError
)
from typing import List, Union, Dict, Any, Tuple, Optional

class RhythmNote(BaseModel):
    position: float = Field(ge=0.0)
    duration: float = Field(gt=0.0)
    velocity: int = Field(default=64, ge=0, le=127)
    accent: bool = False
    tuplet_ratio: Tuple[int, int] = (1, 1)
    groove_offset: float = Field(default=0.0, ge=-1.0, le=1.0)
    groove_velocity: float = Field(default=1.0, ge=0.0, le=2.0)

    def get_actual_position(self) -> float:
        return self.position + self.groove_offset

    def get_actual_velocity(self) -> int:
        velocity_multiplier = 1.2 if self.accent else 1.0
        return min(127, round(self.velocity * self.groove_velocity * velocity_multiplier))

    def get_actual_duration(self) -> float:
        num, den = self.tuplet_ratio
        return self.duration * den / num

    @field_validator('tuplet_ratio')
    def validate_tuplet_ratio(cls, v):
        num, den = v
        if num <= 0 or den <= 0:
            raise ValueError("Tuplet ratio components must be positive")
        if num < den:
            raise ValueError("First number must be greater than or equal to second")
        return v

class RhythmPattern(BaseModel):
    name: str
    pattern: List[Union[Dict[str, Any], RhythmNote]]
    time_signature: str
    description: str = ""
    complexity: float = Field(default=0.5, ge=0.0, le=1.0)
    data: Dict[str, Any] = {}
    groove_template: Optional[Dict[str, List[float]]] = None

    @field_validator('pattern', mode='before')
    @classmethod
    def validate_pattern(cls, v):
        if isinstance(v, list):
            return [
                item if isinstance(item, (dict, RhythmNote)) 
                else item.dict() if hasattr(item, 'dict') 
                else dict(item)
                for item in v
            ]
        raise ValueError("Pattern must be a list")

    @field_validator('time_signature')
    @classmethod
    def validate_time_signature(cls, v):
        try:
            num, den = map(int, v.split('/'))
            if num <= 0 or den <= 0:
                raise ValueError("Time signature components must be positive")
            if den not in [2, 4, 8, 16]:
                raise ValueError("Denominator must be 2, 4, 8, or 16")
            if num not in [2, 3, 4, 6, 9, 12]:
                raise ValueError("Numerator must be 2, 3, 4, 6, 9, or 12 for simple and compound meters")
            return v
        except ValueError as e:
            raise ValueError(str(e))

    @model_validator(mode='after')
    def validate_pattern_duration(self) -> 'RhythmPattern':
        if not self.time_signature:
            return self
        
        num_beats = int(self.time_signature.split('/')[0])
        
        if not self.pattern:
            raise ValueError(f"Pattern must contain at least one note for time signature {self.time_signature}")
        
        last_note = self.pattern[-1]
        if isinstance(last_note, dict):
            last_position = last_note['position']
        else:
            last_position = last_note.position
            
        if last_position < num_beats - 1:
            raise ValueError(f"Pattern duration must be at least {num_beats} beats for time signature {self.time_signature}")
        
        return self

    @model_validator(mode='after')
    def validate_compound_meter_accents(self) -> 'RhythmPattern':
        if not self.time_signature:
            return self
            
        num, den = map(int, self.time_signature.split('/'))
        
        # Check for compound meters (6/8, 9/8, 12/8)
        if den == 8 and num in [6, 9, 12]:
            # Check accents at the start of each group of three
            for i in range(0, num, 3):
                if i >= len(self.pattern):
                    raise ValueError(f"Pattern too short for time signature {self.time_signature}")
                
                # Get the note at the start of each group
                note = self.pattern[i]
                if isinstance(note, dict):
                    note = RhythmNote(**note)
                
                # Verify accent
                if not note.accent:
                    raise ValueError(f"Missing expected accent at position {i} in compound meter {self.time_signature}")
        
        return self

    def apply_groove_template(self, groove_template: Dict[str, List[float]]) -> 'RhythmPattern':
        """Apply a groove template to the pattern."""
        if len(groove_template['timing']) != len(groove_template['velocity']):
            raise ValueError("Timing and velocity lists must have the same length")

        # Create a new pattern with groove applied
        new_pattern = []
        for i, note in enumerate(self.pattern):
            groove_idx = i % len(groove_template['timing'])
            
            # Convert dict to RhythmNote if necessary
            if isinstance(note, dict):
                note = RhythmNote(**note)
            
            # Create new note with groove applied
            new_note = RhythmNote(
                position=note.position,
                duration=note.duration,
                velocity=note.velocity,
                accent=note.accent,
                tuplet_ratio=note.tuplet_ratio,
                groove_offset=groove_template['timing'][groove_idx],
                groove_velocity=groove_template['velocity'][groove_idx]
            )
            new_pattern.append(new_note)

        return RhythmPattern(
            name=self.name,
            pattern=new_pattern,
            time_signature=self.time_signature,
            description=self.description,
            complexity=self.complexity,
            data=self.data,
            groove_template=groove_template
        )
