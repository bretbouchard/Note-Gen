from __future__ import annotations
import logging
import sys
import re
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, field_validator, model_validator, ValidationError, Field, ConfigDict
import uuid
from src.note_gen.models.note import Note

# Ensure logger is set up correctly
logger = logging.getLogger(__name__)


class RhythmNote(BaseModel):
    """Represents a single note in a rhythm pattern."""
    position: float = Field(..., description="Position in beats", ge=0.0)
    duration: float = Field(..., description="Duration in beats", gt=0.0)
    velocity: int = Field(100, description="Note velocity (0-127)", ge=0, le=127)
    is_rest: bool = Field(False, description="Whether this is a rest")
    pitch: Optional[int] = Field(None, description="MIDI pitch number (0-127)", ge=0, le=127)
    accent: Optional[float] = Field(None, description="Accent value (0.0-2.0)", ge=0.0, le=2.0)
    swing_ratio: float = Field(default=0.67, ge=0.5, le=0.75, description="Swing ratio (0.5-0.75)")

    @field_validator('position')
    def validate_position(cls, value):
        if value < 0:
            raise ValueError("Position must be non-negative")
        return value

    @field_validator('duration')
    def validate_duration(cls, value):
        if value <= 0:
            raise ValueError("Duration must be positive")
        return value

    @field_validator('velocity')
    def validate_velocity(cls, value):
        if not 0 <= value <= 127:
            raise ValueError("Velocity must be between 0 and 127")
        return value

    @field_validator('pitch')
    def validate_pitch(cls, value):
        if value is not None and not 0 <= value <= 127:
            raise ValueError("Pitch must be between 0 and 127")
        return value

    @field_validator('accent')
    def validate_accent(cls, value):
        if value is not None and not 0.0 <= value <= 2.0:
            raise ValueError("Accent must be between 0.0 and 2.0")
        return value

    @field_validator('swing_ratio')
    def validate_swing_ratio(cls, value):
        if not 0.5 <= value <= 0.75:
            raise ValueError("Swing ratio must be between 0.5 and 0.75")
        return value

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPatternData(BaseModel):
    """Represents the data for a rhythm pattern."""
    notes: List[RhythmNote] = Field(
        ..., 
        description="List of rhythm notes",
        min_length=1,
        error_messages={"min_length": "At least one note is required"}
    )
    time_signature: str = Field(
        default="4/4",
        pattern=r"^\d+/\d+$",
        description="Time signature (e.g., '4/4', '3/4')"
    )
    swing_enabled: bool = Field(default=False, description="Whether swing is enabled")
    humanize_amount: float = Field(default=0.0, ge=0.0, le=1.0, description="Amount of humanization to apply")
    swing_ratio: float = Field(default=0.67, ge=0.5, le=0.75, description="Swing ratio (0.5-0.75)")
    default_duration: float = Field(
        default=1.0, 
        gt=0.0,
        description="Default note duration",
        error_messages={"gt": "Default duration must be positive"}
    )
    total_duration: float = Field(default=4.0, gt=0.0, description="Total duration of the pattern")
    accent_pattern: List[str] = Field(default_factory=list, description="Pattern of accents")
    groove_type: str = Field(default="straight", description="Type of groove")
    variation_probability: float = Field(default=0.0, ge=0.0, le=1.0, description="Probability of variations")
    duration: float = Field(default=1.0, gt=0.0, description="Duration in beats")
    style: str = Field(default="basic", description="Musical style")

    @field_validator('time_signature')
    def validate_time_signature(cls, value):
        try:
            numerator, denominator = map(int, value.split('/'))
            if numerator <= 0 or denominator <= 0:
                raise ValueError("Both numerator and denominator must be positive")
            # Check if denominator is a power of 2
            if denominator & (denominator - 1) != 0:
                raise ValueError("Time signature denominator must be a positive power of 2")
            return value
        except ValueError as e:
            raise ValueError(f"Invalid time signature format: {str(e)}")

    @field_validator('groove_type')
    def validate_groove_type(cls, value):
        valid_types = ["straight", "swing", "shuffle"]
        if value not in valid_types:
            raise ValueError(f"Invalid groove type. Must be one of: {', '.join(valid_types)}")
        return value

    @field_validator('notes')
    def validate_notes(cls, value):
        if not value:
            raise ValueError("At least one note is required")
        
        # Sort notes by position for easier validation
        sorted_notes = sorted(value, key=lambda x: x.position)
        
        # Check for overlapping notes
        for i in range(len(sorted_notes) - 1):
            current_note = sorted_notes[i]
            next_note = sorted_notes[i + 1]
            current_end = current_note.position + current_note.duration
            
            if current_end > next_note.position:
                raise ValueError(f"Notes overlap at position {next_note.position}")
        
        return value

    @field_validator('accent_pattern')
    def validate_accent_pattern(cls, value):
        for accent in value:
            try:
                accent_value = float(accent)
                if not 0.0 <= accent_value <= 2.0:
                    raise ValueError("Accent values must be between 0.0 and 2.0")
            except ValueError:
                raise ValueError("Invalid accent value. Must be a float between 0.0 and 2.0")
        return value

    @model_validator(mode='after')
    def calculate_total_duration(cls, values):
        values.total_duration = sum(note.duration for note in values.notes)  # Update to correctly sum durations
        return values

    @model_validator(mode='after')
    def validate_total_duration(cls, values):
        """Validate total duration."""
        if not values.notes:
            return values
            
        if values.total_duration < 0:
            raise ValueError("Total duration cannot be negative")
            
        # Get time signature components
        numerator, denominator = map(int, values.time_signature.split('/'))
        beat_duration = 4.0 / denominator
        
        # Ensure total duration is a multiple of the beat duration
        remainder = values.total_duration % beat_duration
        if remainder > 0.0001:  # Use small epsilon for float comparison
            raise ValueError(f"Total duration must be a multiple of the beat duration ({beat_duration})")
            
        return values

    @model_validator(mode='after')
    def validate_note_positions(cls, values):
        """Validate note positions."""
        if not values.notes:
            return values
            
        # Sort notes by position
        sorted_notes = sorted(values.notes, key=lambda x: x.position)
        
        # Check for overlapping notes
        for i in range(len(sorted_notes) - 1):
            current_note = sorted_notes[i]
            next_note = sorted_notes[i + 1]
            
            if current_note.position + current_note.duration > next_note.position:
                raise ValueError("Notes cannot overlap")
                
        return values

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPattern(BaseModel):
    """Represents a pattern for generating rhythmic notes."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description='Pattern ID')
    name: str = Field(
        ..., 
        description='Pattern name',
        min_length=1,
        max_length=100,
        error_messages={"min_length": "Name cannot be empty"}
    )
    data: RhythmPatternData = Field(..., description='Pattern data')
    description: str = Field(default='', description='Pattern description')
    tags: List[str] = Field(
        default_factory=list,
        description='Tags for categorization',
        min_length=1,
        error_messages={"min_length": "Tags cannot be None or an empty list"}
    )
    complexity: float = Field(default=1.0, ge=0.0, le=10.0, description='Pattern complexity score (1-10)')
    style: Optional[str] = Field(None, description='Musical style (e.g., jazz, rock)')
    pattern: str = Field(default='4 4', description='String representation of the rhythm pattern')
    is_test: bool = Field(default=False)

    @model_validator(mode='after')
    def validate_data(cls, values):
        data = values.data  # Access directly from the instance
        if not isinstance(data, RhythmPatternData):
            raise ValueError('data must be a valid RhythmPatternData instance')
        if not data.notes:
            raise ValueError('data.notes is required and cannot be empty')
        if not all(isinstance(note, RhythmNote) for note in data.notes):
            raise ValueError('All notes in data.notes must be valid RhythmNote instances')
        if not all(note.position >= 0 for note in data.notes):
            raise ValueError('All note positions must be non-negative')
        if not all(note.duration > 0 for note in data.notes):
            raise ValueError('All note durations must be positive')
        if not all(0 <= note.velocity <= 127 for note in data.notes):
            raise ValueError('All note velocities must be between 0 and 127')
        if not all(note.pitch is None or 0 <= note.pitch <= 127 for note in data.notes):
            raise ValueError('All note pitches must be between 0 and 127')
        if not all(note.accent is None or 0.0 <= note.accent <= 2.0 for note in data.notes):
            raise ValueError('All note accents must be between 0.0 and 2.0')
        if not all(0.5 <= note.swing_ratio <= 0.75 for note in data.notes):
            raise ValueError('All note swing ratios must be between 0.5 and 0.75')
        return values

    @staticmethod
    def _calculate_note_duration(note: str) -> float:
        """Calculate the duration of a note in beats.
        
        Args:
            note: A string representing the note duration (e.g., '4', '8.', '16')
            
        Returns:
            The duration of the note in beats
            
        Raises:
            ValueError: If the note duration is invalid
        """
        base_duration = float(note.rstrip('.'))
        if base_duration <= 0:
            raise ValueError("Note duration must be positive")
            
        # Convert note value to beats (e.g., 4 = 1.0 beats, 8 = 0.5 beats)
        duration = 4.0 / base_duration
        if '.' in note:
            # A dotted note is 1.5 times its normal duration
            duration *= 1.5
        return duration

    @field_validator('pattern')
    def validate_pattern(cls, value):
        """Validate the rhythm pattern string."""
        if not value:
            raise ValueError("Pattern cannot be empty")
            
        # Pattern should be space-separated numbers, optionally with dots
        pattern_regex = r'^(\d+\.?\s*)+$'
        if not re.match(pattern_regex, value):
            raise ValueError("Invalid pattern format. Pattern should be space-separated numbers (e.g., '4 4' or '8. 16')")
            
        # Convert pattern to durations to validate
        try:
            for note in value.strip().split():
                cls._calculate_note_duration(note)
        except ValueError as e:
            raise ValueError(f"Invalid pattern: {str(e)}")
            
        return value

    @model_validator(mode='after')
    def validate_pattern_with_time_signature(cls, values):
        """Validate that the pattern matches the time signature, allowing for flexible durations."""
        try:
            # Get time signature components
            numerator, denominator = map(int, values.data.time_signature.split('/'))
            beat_duration = 4.0 / denominator  # Quarter note duration
            measure_duration = numerator * beat_duration  # Duration of one measure
            
            # Calculate total duration from pattern
            durations = [cls._calculate_note_duration(note) for note in values.pattern.strip().split()]
            total_duration = sum(durations)
            
            # Allow patterns to be any duration
            # Optionally, you could log the total duration for reference
            print(f"Total duration of the pattern: {total_duration:.2f} beats")
            
            return values
        except Exception as e:
            raise ValueError(f"Error validating pattern with time signature: {str(e)}")

    def get_events_in_range(
        self, start_position: float, end_position: float
    ) -> List[RhythmNote]:
        """Get all notes within a specified range of positions."""
        if start_position < 0:
            raise ValueError("Start position cannot be negative")
        if end_position < start_position:
            raise ValueError("End position must be greater than start position")
            
        return [
            note for note in self.data.notes
            if start_position <= note.position < end_position
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
            duration = self._calculate_note_duration(part)
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

    def recalculate_pattern_duration(self, total_duration: float) -> None:
        """Recalculate the total duration of the rhythm pattern based on the notes."""
        self.data.total_duration = sum(note.duration for note in self.data.notes)
        if self.data.total_duration != total_duration:
            raise ValueError("Total duration must be a multiple of the beat duration")

    def __str__(self) -> str:
        """Get string representation of the rhythm pattern."""
        return f"RhythmPattern(name={self.name}, total_duration={self.data.total_duration})"

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmNoteSimple(BaseModel):
    """Class representing a single note in a rhythm pattern."""
    duration: float
    is_rest: bool = False
    velocity: float = 1.0
    
    @field_validator('duration')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v
    
    @field_validator('velocity')
    def validate_velocity(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Velocity must be between 0 and 1")
        return v

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPatternSimple(BaseModel):
    """Class representing a rhythm pattern."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    pattern: List[RhythmNoteSimple]
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    complexity: float = 1.0
    is_test: bool = Field(default=False)

    @field_validator('pattern')
    def validate_pattern(cls, v):
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
        return sum(note.velocity for note in self.pattern if not note.is_rest) / len(active_notes)

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

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPatternResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID of the rhythm pattern")
    name: str = Field(description="Name of the rhythm pattern")
    pattern: List[Union[Note, int]] = Field(description="List of notes in the rhythm pattern")
    description: str = Field(description="Description of the rhythm pattern")
    tags: List[str] = Field(..., description="Tags for the rhythm pattern")
    complexity: Optional[float] = Field(None, description="Complexity rating of the rhythm pattern")

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )