from __future__ import annotations
import logging
import sys
import re
from typing import List, Optional, Type, Any
from pydantic import BaseModel, Field, validator, field_validator, model_validator
import uuid

# Configure logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RhythmNote(BaseModel):
    """A single note in a rhythm pattern."""

    def __init__(
        self,
        *,
        position: float = 0.0,
        duration: float = 1.0,
        velocity: int = 100,
        is_rest: bool = False,
        accent: Optional[int] = None,
        swing_ratio: Optional[float] = None,
    ) -> None:
        super().__init__(
            position=position,
            duration=duration,
            velocity=velocity,
            is_rest=is_rest,
            accent=accent,
            swing_ratio=swing_ratio,
        )

    position: float = Field(0.0, description="Position in beats")
    duration: float = Field(1.0, description="Duration in beats")
    velocity: int = Field(100, description="Note velocity (0-127)")
    is_rest: bool = Field(False, description="Indicates if the note is a rest")
    accent: Optional[int] = Field(
        None, description="Note accent (e.g., staccato, legato, accent)"
    )
    swing_ratio: Optional[float] = Field(
        None, description="Swing ratio for this note (0.5-0.75)"
    )
    @field_validator("position")
    def validate_position(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Position must be non-negative.")
        return value

    @field_validator("duration")
    def validate_duration(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Duration must be positive.")
        return value

    @field_validator("velocity")
    def validate_velocity(cls, value: int) -> int:
        if not (0 <= value <= 127):
            raise ValueError("Velocity must be between 0 and 127.")
        return value

    @field_validator("swing_ratio")
    def validate_swing_ratio(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not (0.5 <= value <= 0.75):
            raise ValueError("Swing ratio must be between 0.5 and 0.75.")
        return value


class RhythmPatternData(BaseModel):
    """Data class for rhythm pattern data."""
    notes: List[RhythmNote]
    time_signature: str = "4/4"
    swing_enabled: bool = False
    humanize_amount: float = 0.0
    swing_ratio: float = 0.67
    default_duration: float = 1.0
    total_duration: float = 4.0
    accent_pattern: List[float] = Field(default_factory=list)
    groove_type: str = "straight"
    variation_probability: float = 0.0
    duration: float = 1.0
    style: str = "basic"

    def calculate_total_duration(self) -> None:
        """Calculate and update the total duration based on note positions and durations."""
        if not self.notes:
            self.total_duration = 0.0
            return

        max_duration = 0.0
        for note in self.notes:
            note_end = note.position + note.duration
            max_duration = max(max_duration, note_end)
        
        self.total_duration = max_duration

    @model_validator(mode="after")
    def validate_model(self) -> "RhythmPatternData":
        """Validate the model after creation."""
        self.calculate_total_duration()
        return self

    @field_validator("time_signature")
    def validate_time_signature(cls, v: str) -> str:
        """Validate time signature format."""
        valid_signatures = ["2/4", "3/4", "4/4", "6/8", "9/8", "12/8"]
        try:
            numerator, denominator = map(int, v.split("/"))
            if numerator <= 0 or denominator <= 0:
                raise ValueError
            if denominator not in [1, 2, 4, 8, 16, 32]:
                raise ValueError
            if numerator not in [2, 3, 4, 6, 8, 9, 12]:
                raise ValueError
            if v not in valid_signatures:
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError("Invalid time signature. Must be in format: numerator/denominator where numerator is one of [2,3,4,6,8,9,12] and denominator is a power of 2")
        return v

    @field_validator("groove_type")
    def validate_groove_type(cls, v: str) -> str:
        """Validate groove type."""
        valid_types = ["straight", "swing"]
        if v not in valid_types:
            raise ValueError(f"Groove type must be either 'straight' or 'swing'")
        return v

    @field_validator("default_duration")
    def validate_default_duration(cls, v: float) -> float:
        """Validate default duration."""
        if v <= 0:
            raise ValueError("Default duration must be a positive float.")
        return v

    @field_validator("notes")
    def validate_notes(cls, v: List[RhythmNote]) -> List[RhythmNote]:
        """Validate notes list."""
        if not v:
            raise ValueError("Notes cannot be empty.")
        return v

    @field_validator("humanize_amount")
    def validate_humanize_amount(cls, v: float) -> float:
        """Validate humanize amount."""
        if not 0 <= v <= 1:
            raise ValueError("Humanize amount must be between 0 and 1")
        return v

    @field_validator("swing_ratio")
    def validate_swing_ratio(cls, v: float) -> float:
        """Validate swing ratio."""
        if not 0.5 <= v <= 0.75:
            raise ValueError("Swing ratio must be between 0.5 and 0.75")
        return v

    @field_validator("total_duration")
    def validate_total_duration(cls, v: float) -> float:
        """Validate total duration."""
        if v < 0:
            raise ValueError("Total duration must be positive")
        return v

    @field_validator("style")
    def validate_style(cls, v: str) -> str:
        """Validate style."""
        valid_styles = ["basic", "jazz", "rock", "latin", "funk"]
        if v not in valid_styles:
            raise ValueError(f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        return v

    @field_validator("accent_pattern")
    def validate_accent_pattern(cls, v: List[float]) -> List[float]:
        """Validate accent pattern."""
        for accent in v:
            if not isinstance(accent, float) or not 0 <= accent <= 1:
                raise ValueError("Accent values must be floats between 0 and 1")
        return v

    @field_validator("variation_probability")
    def validate_variation_probability(cls, v: float) -> float:
        """Validate variation probability."""
        if not 0 <= v <= 1:
            raise ValueError("Variation probability must be between 0 and 1")
        return v

    @field_validator("duration")
    def validate_duration(cls, v: float) -> float:
        """Validate duration."""
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v


class RhythmPattern(BaseModel):
    """Represents a pattern for generating rhythmic notes."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    data: RhythmPatternData
    description: Optional[str] = Field("", description="Pattern description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    complexity: float = Field(1.0, description="Pattern complexity score (1-10)")
    style: Optional[str] = Field(None, description="Musical style (e.g., jazz, rock)")
    pattern: str = Field(description="String representation of the rhythm pattern")
    is_test: bool = Field(default=False)

    class Config:
        schema_extra = {
            'example': {
                'id': '1',
                'name': 'quarter_notes',
                'data': {'notes': [{'duration': 1.0, 'velocity': 100}], 'time_signature': '4/4'}
            }
        }

    def __init__(
        self,
        *,
        id: str,
        name: str,
        data: RhythmPatternData,
        description: Optional[str] = "",
        tags: List[str] = [],
        complexity: float = 1.0,
        style: Optional[str] = None,
        pattern: str = "",
        is_test: bool = False,
    ) -> None:
        if not isinstance(data, RhythmPatternData):
            raise TypeError("data must be an instance of RhythmPatternData")
        super().__init__(
            id=id,
            name=name,
            data=data,
            description=description,
            tags=tags,
            complexity=complexity,
            style=style,
            pattern=pattern,
            is_test=is_test,
        )

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        return value

    @field_validator("data")
    def validate_data(cls, data: RhythmPatternData) -> RhythmPatternData:
        if not isinstance(data, RhythmPatternData):
            raise TypeError("Data must be a RhythmPatternData object.")
        if not data.notes:
            raise ValueError("RhythmPatternData must contain at least one note.")
        return data

    @field_validator("pattern")
    def validate_pattern(cls, value: str) -> str:
        if not re.match(r'^[1-9\.\- ]+$', value):  
            raise ValueError("Pattern can only contain numbers 1-9, dots (.), hyphens (-), and spaces.")
        return value

    def get_events_in_range(
        self, start_position: float, end_position: float
    ) -> List[RhythmNote]:
        """Get all notes within a specified range of positions."""
        return [
            note
            for note in self.data.notes
            if note.position < end_position
            and (note.position + note.duration) > start_position
        ]

    def get_pattern_duration(self) -> float:
        """Recalculate and return the total duration of the rhythm pattern."""
        self.data.calculate_total_duration()
        return self.data.total_duration

    def get_durations(self) -> List[float]:
        """Convert the pattern string to a list of note durations.
        
        Returns:
            List[float]: List of note durations in beats
        """
        durations = []
        parts = self.pattern.split()
        
        for part in parts:
            # Handle tied notes
            if '-' in part:
                tied_notes = part.split('-')
                duration = sum(self._get_single_duration(note) for note in tied_notes)
                durations.append(duration)
            else:
                duration = self._get_single_duration(part)
                durations.append(duration)
                
        return durations
    
    def _get_single_duration(self, note: str) -> float:
        """Calculate the duration of a single note.
        
        Args:
            note: String representation of the note (e.g., "4" or "4.")
            
        Returns:
            float: Duration in beats
        """
        base_duration = 4 / int(note[0])  # Convert to fraction of whole note
        
        # Handle dotted notes
        if note.endswith('.'):
            return base_duration * 1.5  # Dotted note is 1.5x the base duration
            
        return base_duration
    
    def __str__(self) -> str:
        """Get string representation of the rhythm pattern."""
        return self.pattern
