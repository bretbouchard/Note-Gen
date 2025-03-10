from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Union

class RhythmPattern(BaseModel):
    pattern: List[float] = Field(
        default_factory=list,
        description='Rhythm pattern as list of float durations'
    )

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: Union[str, List[float]]) -> List[float]:
        if isinstance(v, str):
            try:
                return [float(x) for x in v.split()]
            except ValueError as exc:
                raise ValueError('Pattern string must contain space-separated numbers') from exc
        elif isinstance(v, list):
            if not all(isinstance(x, (int, float)) for x in v):
                raise ValueError('Pattern list must contain only numbers')
            return [float(x) for x in v]
        raise ValueError('Pattern must be string or list of numbers')

    @model_validator(mode='after')
    def validate_pattern_required(self) -> 'RhythmPattern':
        if not self.pattern:
            raise ValueError('Pattern cannot be empty')
        return self

    def __str__(self) -> str:
        return ' '.join(str(x) for x in self.pattern)
