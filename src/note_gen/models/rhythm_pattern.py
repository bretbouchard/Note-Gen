from __future__ import annotations
import logging
import sys
import re
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, field_validator, model_validator
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
    time_signature: str = Field(
        "4/4", 
        description="Time signature in format 'numerator/denominator'",
        pattern=r'^\d+/\d+$',
        frozen=True
    )
    swing_enabled: bool = False
    humanize_amount: float = 0.0
    swing_ratio: float = 0.67
    default_duration: float = 1.0
    total_duration: float = Field(default=0.0, description="Total duration in beats")
    accent_pattern: List[float] = Field(default_factory=list)
    groove_type: str = "straight"
    variation_probability: float = 0.0
    duration: float = 1.0
    style: str = "basic"

    @field_validator("time_signature")
    @classmethod
    def validate_time_signature(cls, value: str) -> str:
        try:
            numerator, denominator = map(int, value.split('/'))
            # Check if numerator is positive
            if numerator <= 0:
                raise ValueError("Time signature numerator must be positive")
            
            # Check if denominator is a power of 2
            if denominator <= 0 or (denominator & (denominator - 1)) != 0:
                raise ValueError("Time signature denominator must be a positive power of 2")
            return value
        except ValueError as e:
            if str(e).startswith("Time signature"):
                raise
            raise ValueError("Invalid time signature format")

    @model_validator(mode='after')
    def validate_model(self) -> 'RhythmPatternData':
        """Validate the model after creation."""
        self.total_duration = self.calculate_total_duration()
        return self

    def calculate_total_duration(self) -> float:
        """Calculate and update the total duration based on note positions and durations."""
        if not self.notes:
            return 0.0
        return max(note.position + note.duration for note in self.notes)

    @field_validator('groove_type')
    def validate_groove_type(cls, v: str) -> str:
        """Validate groove type."""
        valid_types = ["straight", "swing"]
        if v not in valid_types:
            raise ValueError("Groove type must be either 'straight' or 'swing'")
        return v

    @field_validator("default_duration")
    def validate_default_duration(cls, v: float) -> float:
        """Validate default duration."""
        if v <= 0:
            raise ValueError("Default duration must be positive")
        return v

    @field_validator("notes")
    def validate_notes(cls, v: List[RhythmNote]) -> List[RhythmNote]:
        """Validate notes list."""
        if not v:
            raise ValueError("Notes list cannot be empty")
        return v

    @field_validator("humanize_amount")
    def validate_humanize_amount(cls, v: float) -> float:
        """Validate humanize amount."""
        if not 0.0 <= v <= 1.0:
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
            raise ValueError("Total duration must be non-negative")
        return v

    @field_validator("style")
    def validate_style(cls, v: str) -> str:
        """Validate style."""
        valid_styles = ["basic", "jazz", "rock", "latin", "funk"]
        if v not in valid_styles:
            raise ValueError(f"Invalid style. Must be one of {valid_styles}")
        return v

    @field_validator("accent_pattern", mode="before")
    def validate_accent_pattern(cls, v: List[Any]) -> List[float]:
        """Validate accent pattern."""
        try:
            values = [float(x) for x in v]
            if any(not 0.0 <= x <= 1.0 for x in values):
                raise ValueError("Accent values must be floats between 0 and 1")
            return values
        except (ValueError, TypeError):
            raise ValueError("Accent values must be floats between 0 and 1")

    @field_validator("variation_probability")
    def validate_variation_probability(cls, v: float) -> float:
        """Validate variation probability."""
        if not 0.0 <= v <= 1.0:
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

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    data: RhythmPatternData
    description: Optional[str] = Field("", description="Pattern description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    complexity: float = Field(1.0, description="Pattern complexity score (1-10)")
    style: Optional[str] = Field(None, description="Musical style (e.g., jazz, rock)")
    pattern: str = Field(default="", description="String representation of the rhythm pattern")
    is_test: bool = Field(default=False)

    @model_validator(mode='before')
    def validate_data(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert data field."""
        if 'data' in values and not isinstance(values['data'], RhythmPatternData):
            if isinstance(values['data'], dict):
                values['data'] = RhythmPatternData(**values['data'])
        return values

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        """Validate name."""
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("pattern")
    def validate_pattern(cls, value: str) -> str:
        """Validate pattern string."""
        if value and not re.match(r"^[1-9\.\- ]+$", value):
            raise ValueError("Pattern can only contain numbers 1-9, dots (.), hyphens (-), and spaces.")
        return value

    def get_events_in_range(
        self, start_position: float, end_position: float
    ) -> List[RhythmNote]:
        """Get all notes within a specified range of positions."""
        return [
            note
            for note in self.data.notes
            if note.position >= start_position and note.position < end_position
        ]

    def get_pattern_duration(self) -> float:
        """Recalculate and return the total duration of the rhythm pattern."""
        return self.data.total_duration

    def get_durations(self) -> List[float]:
        """Convert the pattern string to a list of note durations.
        
        Returns:
            List[float]: List of note durations in beats
        """
        if not self.pattern:
            return []

        durations = []
        pattern_parts = self.pattern.split()
        for part in pattern_parts:
            duration = self._get_single_duration(part)
            if duration > 0:
                durations.append(duration)

        return durations

    def _get_single_duration(self, note: str) -> float:
        """Calculate the duration of a single note.
        
        Args:
            note: String representation of the note (e.g., "4" or "4.")
            
        Returns:
            float: Duration in beats
        """
        try:
            base_duration = float(note.rstrip("."))
            if base_duration <= 0:
                return 0.0

            duration = 1.0 / base_duration
            if note.endswith("."):
                duration *= 1.5

            return duration
        except ValueError:
            return 0.0

    def __str__(self) -> str:
        """Get string representation of the rhythm pattern."""
        return f"RhythmPattern(name={self.name}, total_duration={self.data.total_duration})"


class RhythmNoteSimple(BaseModel):
    """Class representing a single note in a rhythm pattern."""
    duration: float
    is_rest: bool = False
    velocity: float = 1.0
    
    @field_validator("duration")
    def validate_duration(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v
    
    @field_validator("velocity")
    def validate_velocity(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Velocity must be between 0 and 1")
        return v


class RhythmPatternSimple(BaseModel):
    """Class representing a rhythm pattern."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    pattern: List[RhythmNoteSimple]
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    complexity: float = 1.0
    is_test: bool = Field(default=False)

    @field_validator("pattern")
    def validate_pattern(cls, v: List[Any]) -> List[RhythmNoteSimple]:
        if not isinstance(v, list):
            raise ValueError("Pattern must be a list")
        
        validated_notes = []
        for note in v:
            if isinstance(note, RhythmNoteSimple):
                validated_notes.append(note)
            elif isinstance(note, dict):
                validated_notes.append(RhythmNoteSimple(**note))
            else:
                raise ValueError(f"Invalid note type: {type(note)}")
        return validated_notes

    def get_total_duration(self) -> float:
        """Get the total duration of the rhythm pattern."""
        return sum(note.duration for note in self.pattern)

    def get_note_count(self) -> int:
        """Get the number of notes in the pattern."""
        return len(self.pattern)

    def get_rest_count(self) -> int:
        """Get the number of rests in the pattern."""
        return sum(1 for note in self.pattern if note.is_rest)

    def get_active_note_count(self) -> int:
        """Get the number of active (non-rest) notes in the pattern."""
        return sum(1 for note in self.pattern if not note.is_rest)

    def get_average_velocity(self) -> float:
        """Get the average velocity of notes in the pattern."""
        active_notes = [note for note in self.pattern if not note.is_rest]
        if not active_notes:
            return 0.0
        return sum(note.velocity for note in active_notes) / len(active_notes)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the rhythm pattern to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "pattern": [
                {
                    "duration": note.duration,
                    "is_rest": note.is_rest,
                    "velocity": note.velocity
                }
                for note in self.pattern
            ],
            "description": self.description,
            "tags": self.tags,
            "complexity": self.complexity,
            "is_test": self.is_test
        }

    def __str__(self) -> str:
        """Get string representation of the rhythm pattern."""
        return f"{self.name}: {' '.join(str(note.duration) for note in self.pattern)}"

class RhythmPatternResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID of the rhythm pattern")
    name: str = Field(description="Name of the rhythm pattern")
    pattern: List[Union[Note, int]] = Field(description="List of notes in the rhythm pattern")
    description: str = Field(description="Description of the rhythm pattern")
    tags: List[str] = Field(..., description="Tags for the rhythm pattern")
    complexity: Optional[float] = Field(None, description="Complexity rating of the rhythm pattern")