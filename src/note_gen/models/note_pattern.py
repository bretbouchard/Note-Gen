"""Data structures for musical note patterns."""

from __future__ import annotations
from uuid import uuid4, UUID
from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from enum import Enum

from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import NotePatternData  # Importing from patterns.py
from src.note_gen.models.scale import Scale  # Importing Scale model

# Type aliases
DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]
NoteType = Union[Note, ScaleDegree, Chord]


class NotePattern(BaseModel):
    """
    Represents a pattern of intervals between notes.
    The 'pattern' field indicates the relative distances between notes,
    rather than actual note values. This class does not include
    specific notes, as it focuses on the structure of the pattern.
    """
    id: Optional[str] = Field(None, description="The unique identifier of the note pattern")
    index: Optional[int] = Field(None, description='Index of the note pattern')
    name: str = Field(..., description="The name of the note pattern")
    pattern: List[int] = Field(..., description="The sequence of intervals that define the pattern")
    direction: str = Field("up", description="The direction of the pattern (up, down, or random)")
    use_chord_tones: bool = Field(False, description="Whether to use chord tones")
    use_scale_mode: bool = Field(True, description="Whether to use scale mode")
    arpeggio_mode: bool = Field(False, description="Whether to use arpeggio mode")
    restart_on_chord: bool = Field(True, description="Whether to restart on chord change")
    description: Optional[str] = Field(None, description="A description of the pattern")
    tags: List[str] = Field(default_factory=list, description="Tags associated with the pattern")
    complexity: Optional[float] = Field(None, description="The complexity rating of the pattern")
    is_test: bool = Field(False, description="Whether this is a test pattern")
    duration: float = Field(1.0, description="The duration of each note in the pattern")
    position: float = Field(0.0, description="The position of the pattern in time")
    velocity: int = Field(64, description="The velocity (loudness) of the notes")
    data: Optional[Union[dict, NotePatternData]] = Field(None, description="Additional data associated with the pattern")

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        extra='allow',  # Allow extra fields for testing
        json_schema_extra={
            "example": {
                "name": "Simple Triad",
                "pattern": [0, 4, 7],
                "direction": "up",
                "description": "A simple major triad pattern",
                "tags": ["triad", "basic"],
                "duration": 1.0,
                "velocity": 64
            }
        }
    )

    def __init__(self, **data: Dict[str, Any]) -> None:
        """
        Custom initialization to handle extra fields for testing.
        Removes extra fields before Pydantic validation.
        """
        # Remove extra fields that aren't part of the model
        allowed_fields = set(self.model_fields.keys())
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # Store the original data
        if 'data' in data:
            filtered_data['data'] = data['data']
        
        # Try to extract pattern from various possible sources
        pattern = None
        
        # First, check if 'pattern' is directly provided
        if 'pattern' in data:
            pattern = data['pattern']
        
        # Next, try to extract from NotePatternData
        elif 'data' in data and hasattr(data['data'], 'pattern'):
            pattern = data['data'].pattern
        
        # If no pattern found, try to generate from notes
        elif 'notes' in data and data['notes']:
            # Assume first note as base, calculate intervals to subsequent notes
            base_note = data['notes'][0]
            intervals = []
            for i in range(1, len(data['notes'])):
                intervals.append(data['notes'][i].midi_number - base_note.midi_number)
            pattern = [0] + intervals  # Include the base note interval
        
        # If still no pattern, use a default
        if pattern is None:
            pattern = [0, 2, 4]  # Default pattern
        
        # Add pattern to filtered data
        filtered_data['pattern'] = pattern

        # Ensure required fields are present
        if 'name' not in filtered_data:
            filtered_data['name'] = 'Test Pattern'
        if 'description' not in filtered_data:
            filtered_data['description'] = 'Auto-generated test pattern'
        if 'tags' not in filtered_data:
            filtered_data['tags'] = ['test']

        # Add default values for missing required fields
        default_fields = {
            'duration': 1.0,
            'position': 0.0,
            'velocity': 64,
            'is_test': True
        }
        for field, default_value in default_fields.items():
            if field not in filtered_data:
                filtered_data[field] = default_value

        super().__init__(**filtered_data)

    def __getattr__(self, item: str) -> Any:
        """
        Custom attribute getter to handle dynamic attributes.
        """
        # If the attribute is 'data' and it's not set, return the original data
        if item == 'data' and hasattr(self, '_data'):
            return self._data
        
        # For other attributes, use the default Pydantic behavior
        raise AttributeError(f'{type(self).__name__!r} object has no attribute {item!r}')

    @field_validator("pattern")
    def validate_pattern(cls, value: List[int]) -> List[int]:
        """Validate the pattern intervals."""
        if not value:
            raise ValueError("Pattern must not be empty")
        if not all(isinstance(i, int) for i in value):
            raise ValueError("All pattern values must be integers")
        if any(abs(i) > 12 for i in value):
            raise ValueError("Interval {} is outside reasonable range".format(max(abs(i) for i in value)))
        return value

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        """Validate the pattern name."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return value.strip()

    @field_validator("velocity")
    def validate_velocity(cls, value: int) -> int:
        """Validate the velocity value."""
        if not 0 <= value <= 127:
            raise ValueError("Velocity must be between 0 and 127")
        return value

    @field_validator("duration")
    def validate_duration(cls, value: float) -> float:
        """Validate the duration value."""
        if value <= 0:
            raise ValueError("Duration must be greater than 0")
        return value

    @field_validator("position")
    def validate_position(cls, value: float) -> float:
        """Validate the position value."""
        if value < 0:
            raise ValueError("Position cannot be negative")
        return value

    @field_validator("complexity")
    def validate_complexity(cls, value: Optional[float]) -> Optional[float]:
        """Validate the complexity value."""
        if value is not None and not (0 <= value <= 1):
            raise ValueError("Complexity must be between 0 and 1")
        return value

    @field_validator("tags")
    def validate_tags(cls, value: List[str]) -> List[str]:
        """Validate the tags."""
        if any(not tag.strip() for tag in value):
            raise ValueError("Tags must contain non-whitespace strings")
        return value

    def add_tag(self, tag: str) -> None:
        """Add a new tag to the pattern."""
        if tag.strip():
            self.tags.append(tag.strip())

    def remove_tag(self, tag: str) -> None:
        """Remove a specific tag from the pattern."""
        self.tags = [t for t in self.tags if t != tag.strip()]

    def get_pattern_duration(self) -> float:
        """Calculate the total duration of the pattern."""
        return self.duration * len(self.pattern)


class NotePatternResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Name is required"}}}, description="Name of the note pattern")
    pattern: List[int] = Field(..., description="The sequence of intervals that define the pattern")
    direction: str = Field("up", description="The direction of the pattern (up, down, or random)")
    use_chord_tones: bool = Field(False, description="Whether to use chord tones")
    use_scale_mode: bool = Field(False, description="Whether to use scale mode")
    arpeggio_mode: bool = Field(False, description="Whether to use arpeggio mode")
    restart_on_chord: bool = Field(False, description="Whether to restart on chord change")
    description: str = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Description is required"}}}, description="Pattern description")
    tags: List[str] = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Tags are required"}}}, description="Pattern tags")
    complexity: Optional[float] = Field(None, description="Pattern complexity")
    is_test: Optional[bool] = Field(default=None, description="Test flag")
    duration: float = Field(1.0, description="The duration of each note in the pattern")
    position: float = Field(0.0, description="The position of the pattern in time")
    velocity: int = Field(64, description="The velocity (loudness) of the notes")
    data: Optional[dict] = Field(None, description="Additional data associated with the pattern")