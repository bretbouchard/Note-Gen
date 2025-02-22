from __future__ import annotations
import logging
import sys
import re
from typing import List, Optional, Any, Dict, Union, Type, Callable
from pydantic import BaseModel, Field, validator, ValidationError, ConfigDict, field_validator, model_validator
import uuid
from src.note_gen.models.note import Note
import json

# Ensure logger is set up correctly
logger = logging.getLogger(__name__)

class RhythmNote(BaseModel):
    """Represents a single note in a rhythm pattern."""
    position: float = Field(..., description="Position in beats", ge=0.0)
    duration: float = Field(..., description="Duration in beats", gt=0.0)
    velocity: float = Field(default=100.0, description="Velocity of the note", ge=0.0, le=127.0)
    is_rest: bool = Field(default=False, description="Whether this is a rest")
    pitch: Optional[int] = Field(default=None, description="MIDI pitch number (0-127)", ge=0, lt=128)
    accent: Optional[float] = Field(default=None, description="Accent value (0.0-2.0)", ge=0.0, lt=2.1)
    swing_ratio: float = Field(default=0.67, ge=0.5, le=0.75, description="Swing ratio (0.5-0.75)")

    @field_validator('position', 'duration', 'velocity', 'pitch', 'accent', 'swing_ratio')
    @classmethod
    def validate_numeric_fields(cls, value: Union[float, int], info: Any) -> Union[float, int]:
        field_name = info.field_name
        if field_name == 'position' and value < 0:
            raise ValueError("Input should be greater than or equal to 0")
        elif field_name == 'duration' and value <= 0:
            raise ValueError("Duration must be positive")
        elif field_name == 'velocity' and (value < 0 or value > 127):
            raise ValueError("Velocity must be between 0 and 127")
        elif field_name == 'pitch' and value is not None and not 0 <= value <= 127:
            raise ValueError("Pitch must be between 0 and 127")
        elif field_name == 'accent' and value is not None and not 0.0 <= value <= 2.0:
            raise ValueError("Accent must be between 0.0 and 2.0")
        elif field_name == 'swing_ratio' and not 0.5 <= value <= 0.75:
            raise ValueError("Input should be less than or equal to 0.75")
        return value

    @field_validator('velocity')
    @classmethod
    def validate_velocity(cls, value: float) -> float:
        """Validate velocity with specific error message."""
        if value < 0:
            raise ValueError("Velocity must be greater than or equal to 0")
        elif value > 127:
            raise ValueError("Velocity must be less than or equal to 127")
        return value

    @field_validator('swing_ratio')
    @classmethod
    def validate_swing_ratio(cls, value: float) -> float:
        """Validate swing ratio with specific error message."""
        if value > 0.75:
            raise ValueError("Input should be less than or equal to 0.75")
        return value

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPatternData(BaseModel):
    """Represents the data for a rhythm pattern."""
    notes: List[RhythmNote] = Field(
        ...,
        description="List of rhythm notes"
    )
    time_signature: str = Field(default="4/4", description="Time signature (e.g., '4/4', '3/4')")
    swing_enabled: bool = Field(default=False, description="Whether swing is enabled")
    humanize_amount: float = Field(default=0.0, ge=0.0, le=1.0, description="Amount of humanization to apply")
    swing_ratio: float = Field(default=0.67, ge=0.5, le=0.75, description="Swing ratio (0.5-0.75)")
    default_duration: float = Field(default=1.0, gt=0.0, description="Default note duration")
    total_duration: float = Field(default=4.0, gt=0.0, description="Total duration of the pattern")
    accent_pattern: List[Union[str, float]] = Field(default_factory=list, description="Pattern of accents")
    groove_type: str = Field(default="straight", description="Type of groove")
    variation_probability: float = Field(default=0.0, ge=0.0, le=1.0, description="Probability of variations")
    duration: float = Field(default=1.0, gt=0.0, description="Duration in beats")
    style: str = Field(default="basic", description="Musical style")

    @field_validator('time_signature')
    @classmethod
    def validate_time_signature(cls, value: str) -> str:
        """Validate time signature format and values."""
        import re
        
        # Check time signature format using regex
        if not re.match(r'^\d+/\d+$', value):
            raise ValueError("String should match pattern 'X/Y'")
        
        try:
            numerator, denominator = map(int, value.split('/'))
            
            # Check both numerator and denominator are positive
            if numerator <= 0 or denominator <= 0:
                raise ValueError("Both numerator and denominator must be positive")
            
            if denominator & (denominator - 1) != 0:  # Check if denominator is not a power of 2
                raise ValueError("Time signature denominator must be a positive power of 2")
            
            return value
        except ValueError as e:
            # If the original error is about format, re-raise it
            if "String should match pattern" in str(e):
                raise
            # If it's about positive values, re-raise that specific message
            if "numerator and denominator must be positive" in str(e):
                raise
            # Otherwise, raise the original error about denominator
            raise

    @field_validator('total_duration')
    @classmethod
    def validate_total_duration(cls, value: float, info: Any) -> float:
        """Validate total duration."""
        if value <= 0:
            raise ValueError("Total duration must be positive")
        
        # Get time signature from the values
        time_signature = info.data.get('time_signature', '4/4')
        try:
            numerator, denominator = map(int, time_signature.split('/'))
            
            # Prevent division by zero
            if denominator == 0:
                raise ValueError("Invalid time signature: denominator cannot be zero")
            
            beat_duration = 4.0 / denominator
            
            # Ensure total duration is a multiple of the beat duration
            remainder = abs(value % beat_duration)
            if remainder > 0.0001:  # Use small epsilon for float comparison
                raise ValueError(f"Total duration must be a multiple of the beat duration ({beat_duration})")
                
            return value
        except (ValueError, ZeroDivisionError):
            raise ValueError("Invalid time signature format. Must be in 'X/Y' format with non-zero denominator.")

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, value: List[RhythmNote], info: Any) -> List[RhythmNote]:
        """Validate notes with more robust checks."""
        allow_empty = info.data.get('allow_empty_notes', False)
        
        if not value or len(value) == 0:
            if not allow_empty:
                raise ValueError("List should have at least 1 item after validation")
        
        # Validate each note
        for note in value:
            if note.duration <= 0:
                raise ValueError("Note duration must be positive")
            if note.velocity < 0 or note.velocity > 127:
                raise ValueError("Note velocity must be between 0 and 127")
        
        # Check for overlapping notes
        sorted_notes = sorted(value, key=lambda x: x.position)
        for i in range(len(sorted_notes) - 1):
            current_note = sorted_notes[i]
            next_note = sorted_notes[i + 1]
            
            if current_note.position + current_note.duration > next_note.position:
                raise ValueError("Notes cannot overlap")
        
        return value

    @field_validator('groove_type')
    @classmethod
    def validate_groove_type(cls, value: str) -> str:
        """Validate groove type."""
        allowed_groove_types = ['straight', 'swing', 'shuffle']
        if value.lower() not in allowed_groove_types:
            raise ValueError(f"Invalid groove type. Must be one of: {', '.join(allowed_groove_types)}")
        return value.lower()

    @field_validator('accent_pattern')
    @classmethod
    def validate_accent_pattern(cls, value: List[Union[str, float]]) -> List[str]:
        """Validate accent pattern."""
        if not value:
            return value
        
        try:
            # Convert values to strings, keeping original input
            converted_values = [str(v) for v in value]
            
            # Validate each value
            for v in converted_values:
                float_val = float(v)
                if float_val < 0 or float_val > 2.0:
                    raise ValueError("Invalid accent value. Must be a float between 0.0 and 2.0")
            
            return converted_values
        except ValueError:
            raise ValueError("Invalid accent value. Must be a float between 0.0 and 2.0")

    def calculate_total_duration(self) -> float:
        """Calculate total duration based on notes."""
        self.total_duration = sum(note.duration for note in self.notes)
        return self.total_duration

    def get_pattern_duration(self) -> float:
        """Calculate pattern duration based on pattern string."""
        # If no notes, try to calculate duration from pattern
        if not self.notes:
            # This requires the method to be called from a RhythmPattern instance
            # that has a pattern attribute
            pattern = getattr(self, 'pattern', None)
            if not pattern:
                return 0.0
            
            # Split the pattern string into individual note durations
            pattern_parts = pattern.split()
            
            # Calculate total duration
            total_duration = sum(
                1.0 / float(part.rstrip(".")) if part.rstrip(".").isdigit() else 0.0 
                for part in pattern_parts
            )
            
            return total_duration
        
        # If notes exist, calculate based on notes
        return self.calculate_total_duration()

    def get_durations(self) -> List[float]:
        """Return a list of durations for each note in the rhythm pattern."""
        return [note.duration for note in self.notes] if self.notes else []

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPattern(BaseModel):
    """Represents a pattern for generating rhythmic notes."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description='Pattern ID')
    name: str = Field(..., description='Pattern name', min_length=1, max_length=100)
    data: RhythmPatternData = Field(..., description='Pattern data', alias="data")
    description: str = Field(default='', description='Pattern description')
    tags: List[str] = Field(default_factory=list, description='Tags for categorization', min_length=1)
    complexity: float = Field(default=1.0, ge=0.0, le=10.0, description='Pattern complexity score (1-10)')
    style: Optional[str] = Field(default='basic', description='Musical style')   
    pattern: Union[str, List[float]] = Field(..., description='Pattern representation, can include decimals and negatives')
    groove_type: str = Field(default='straight', description='Type of groove')
    swing_ratio: Optional[float] = Field(default=0.67, ge=0.5, le=0.75, description='Swing ratio (0.5-0.75)')
    duration: float = Field(default=1.0, gt=0.0, description='Duration in beats')

    @field_validator('data')
    @classmethod
    def validate_data(cls, value: Union[RhythmPatternData, Dict[str, Any]]) -> RhythmPatternData:
        """Validate data is a RhythmPatternData instance."""
        if isinstance(value, dict):
            try:
                value = RhythmPatternData(**value)
            except Exception as e:
                raise ValueError(f"Input should be a valid dictionary or instance of RhythmPatternData: {e}")
        
        if not isinstance(value, RhythmPatternData):
            raise ValueError("Input should be a valid dictionary or instance of RhythmPatternData")
        
        return value

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, value: Union[str, List[float]]) -> Union[str, List[float]]:
        if value is None:
            logger.error("Pattern cannot be None")
            raise ValueError("Pattern cannot be None")
        logger.debug(f"Validating pattern: {value}")  # Log the pattern being validated
        if isinstance(value, str):
            # If the value is a string, validate using regex
            pattern_values = value.split()
            note_pattern = re.compile(r'^(-?\d+(?:\.\d*)?|\d+/\d+)$')
            for note in pattern_values:
                if not note_pattern.match(note):
                    logger.error(f"Invalid pattern format for note: {note}")  # Log the invalid note
                    raise ValueError(f"Invalid pattern format for note: {note}. Must be a number, fraction, or dotted number.")
        elif isinstance(value, list):
            # If the value is a list, ensure all entries are floats or integers
            for note in value:
                if not isinstance(note, (float, int)):
                    logger.error(f"Invalid entry in pattern list: {note}")  # Log the invalid entry
                    raise ValueError(f"All entries in the pattern list must be floats or integers.")
        return value

    @field_validator('swing_ratio')
    @classmethod
    def validate_swing_ratio(cls, value: Optional[float]) -> Optional[float]:
        if value < 0.5 or value > 0.75:
            raise ValueError('Input should be less than or equal to 0.75')
        return value

    @field_validator('groove_type')
    @classmethod
    def validate_groove_type(cls, value: str) -> str:
        if value not in ['straight', 'swing']:
            raise ValueError('Groove type must be either "straight" or "swing"')
        return value

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

    def _calculate_pattern_duration(self) -> float:
        """Calculate pattern duration based on pattern string."""
        if not self.pattern:
            return 0.0
        
        # Split the pattern string into individual note durations
        pattern_parts = self.pattern.split()
        
        # Calculate total duration
        total_duration = sum(self._get_single_duration(part) for part in pattern_parts)
        
        return total_duration

    def get_pattern_duration(self) -> float:
        """Recalculate and return the total duration of the rhythm pattern."""
        # If total_duration is already set, return it
        if self.data.total_duration > 0:
            return self.data.total_duration
        
        # If data has no notes, calculate from pattern
        if not self.data.notes:
            # Calculate duration from pattern
            pattern_parts = self.pattern.split()
            
            # Sum the actual values in the pattern
            total_duration = sum(float(part) for part in pattern_parts)
            
            # Update the total_duration in data
            self.data.total_duration = total_duration
            
            return total_duration
        
        # Otherwise, use the data's method
        return self.data.get_pattern_duration()

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

            # Return the base duration instead of beat fraction
            duration = base_duration
            if note.endswith("."):
                duration *= 1.5

            return duration
        except ValueError:
            return 0.0

    def recalculate_pattern_duration(self, total_duration: float) -> None:
        """Recalculate the total duration of the rhythm pattern based on the notes."""
        self.data.total_duration = self.data.get_pattern_duration()
        if self.data.total_duration != total_duration:
            raise ValueError("Total duration must be a multiple of the beat duration")

    @classmethod
    def validate_pattern_with_time_signature(cls, rhythm_pattern: Union[RhythmPattern, RhythmPatternData]):
        """
        Validate the time signature for the rhythm pattern.
        Uses the validate_time_signature method from RhythmPatternData.
        
        Args:
            rhythm_pattern (Union[RhythmPattern, RhythmPatternData]): The rhythm pattern to validate.
        
        Raises:
            ValueError: If the time signature is invalid.
        """
        # If a RhythmPattern is passed, extract its data
        if isinstance(rhythm_pattern, RhythmPattern):
            rhythm_pattern = rhythm_pattern.data
        
        # Validate time signature
        RhythmPatternData.validate_time_signature(rhythm_pattern.time_signature)
        
        # Validate total duration
        if rhythm_pattern.total_duration <= 0:
            raise ValueError("Total duration must be positive")
        
        # Validate notes
        if not rhythm_pattern.notes:
            raise ValueError("Rhythm pattern must contain at least one note")
        
        # Validate notes fit within total duration
        max_note_position = max(note.position + note.duration for note in rhythm_pattern.notes)
        if max_note_position > rhythm_pattern.total_duration:
            raise ValueError(f"Notes extend beyond total pattern duration. Max note position: {max_note_position}, Total duration: {rhythm_pattern.total_duration}")
        
        return True

    def __str__(self) -> str:
        """Get string representation of the rhythm pattern."""
        return f"RhythmPattern(name={self.name}, total_duration={self.data.total_duration})"

    def get_durations(self) -> List[float]:
        """Return a list of durations for each note in the rhythm pattern."""
        return self.data.get_durations()

    @classmethod
    def from_str(cls, pattern_str: str) -> RhythmPattern:
        print(f"Input to from_str: {pattern_str}")
        try:
            # Parse the JSON string
            pattern_data = json.loads(pattern_str)

            # Extract necessary fields
            name = pattern_data['name']
            time_signature = pattern_data['data'].get('time_signature', "4/4")
            notes_data = pattern_data['data']['notes']

            # Extract additional fields with defaults
            swing_enabled = pattern_data['data'].get('swing_enabled', False)
            humanize_amount = pattern_data['data'].get('humanize_amount', 0.0)
            swing_ratio = pattern_data['data'].get('swing_ratio', 0.67)
            default_duration = pattern_data['data'].get('default_duration', 1.0)
            total_duration = pattern_data['data'].get('total_duration', 4.0)
            accent_pattern = pattern_data['data'].get('accent_pattern', [])
            groove_type = pattern_data['data'].get('groove_type', "straight")
            variation_probability = pattern_data['data'].get('variation_probability', 0.0)
            duration = pattern_data['data'].get('duration', 1.0)
            style = pattern_data['data'].get('style', "basic")

            # Validate extracted fields
            if not isinstance(name, str):
                raise ValueError("Invalid name")

            notes = []
            for note in notes_data:
                if not all(key in note for key in ['position', 'duration', 'velocity', 'is_rest']):
                    raise ValueError("Missing required note data")

                position = note['position']
                duration = note['duration']
                velocity = note['velocity']
                is_rest = note['is_rest']
                notes.append(RhythmNote(
                    position=position,
                    duration=duration,
                    velocity=velocity,
                    is_rest=is_rest
                ))

            # Log the state of RhythmPatternData
            logger.info(f"Creating RhythmPatternData with: notes={notes}, time_signature={time_signature}, swing_enabled={swing_enabled}, humanize_amount={humanize_amount}, swing_ratio={swing_ratio}, default_duration={default_duration}, total_duration={total_duration}, accent_pattern={accent_pattern}, groove_type={groove_type}, variation_probability={variation_probability}, duration={duration}, style={style}")

            print(f"Creating RhythmPatternData with: notes={notes}, time_signature={time_signature}, swing_enabled={swing_enabled}, humanize_amount={humanize_amount}, swing_ratio={swing_ratio}, default_duration={default_duration}, total_duration={total_duration}, accent_pattern={accent_pattern}, groove_type={groove_type}, variation_probability={variation_probability}, duration={duration}, style={style}")

            return cls(
                name=name,
                data=RhythmPatternData(
                    notes=notes,
                    time_signature=time_signature,
                    swing_enabled=swing_enabled,
                    humanize_amount=humanize_amount,
                    swing_ratio=swing_ratio,
                    default_duration=default_duration,
                    total_duration=total_duration,
                    accent_pattern=accent_pattern,
                    groove_type=groove_type,
                    variation_probability=variation_probability,
                    duration=duration,
                    style=style
                )
            )
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")
        except Exception as e:
            raise ValueError(f"Error processing rhythm pattern: {str(e)}")

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPatternCreate(BaseModel):
    name: str = Field(..., description='Name of the rhythm pattern')
    data: RhythmPatternData = Field(..., description='Pattern data')
    is_test: bool = Field(default=False, description='Indicates if this is a test pattern')
    style: str = Field(default='basic', description='Musical style')
    tags: List[str] = Field(default_factory=list, description='Tags for categorization')

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmNoteSimple(BaseModel):
    """Class representing a single note in a rhythm pattern."""
    duration: float = Field(..., description="Duration in beats", gt=0.0)
    is_rest: bool = False
    velocity: float = Field(default=1.0, description="Velocity (0-1)", ge=0.0, le=1.0)
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls: Type['RhythmNoteSimple'], value: float) -> float:
        if value <= 0:
            raise ValueError("Duration must be positive")
        return value
    
    @field_validator('velocity')
    @classmethod
    def validate_velocity(cls: Type['RhythmNoteSimple'], value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("Velocity must be between 0 and 1")
        return value

    class Config:
        model_config = ConfigDict(
            arbitrary_types_allowed=True
        )


class RhythmPatternSimple(BaseModel):
    """Class representing a rhythm pattern."""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description='Pattern name', min_length=1, max_length=100)
    pattern: List[RhythmNoteSimple] = Field(..., description='Pattern', min_length=1)
    description: str = ""
    tags: List[str] = Field(default_factory=list, description='Tags for categorization', min_length=1)
    complexity: float = Field(default=1.0, ge=0.0, lt=11.0, description='Pattern complexity score (1-10)')
    is_test: bool = Field(default=False)

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, value: List[RhythmNoteSimple]) -> List[RhythmNoteSimple]:
        if not isinstance(value, list):
            raise ValueError("Pattern must be a list")
        
        validated_notes = []
        for note in value:
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
    pattern: Optional[List[Union[Note, int]]] = Field(default=None, description="List of notes in the rhythm pattern")
    description: str = Field(default="", description="Description of the rhythm pattern")
    tags: List[str] = Field(default_factory=list, description="Tags for the rhythm pattern")
    complexity: Optional[float] = Field(None, description="Complexity rating of the rhythm pattern")
    data: Optional[RhythmPatternData] = Field(None, description="Detailed rhythm pattern data")
    is_test: bool = Field(default=False, description="Flag to indicate if this is a test pattern")

    @model_validator(mode='before')
    @classmethod
    def prepare_pattern_data(cls, values):
        # If pattern is a string, convert it to a list of integers
        if 'pattern' in values and isinstance(values['pattern'], str):
            values['pattern'] = [int(x) for x in values['pattern'].split()]
        # If pattern is not provided, try to extract from data
        elif 'pattern' not in values and 'data' in values:
            rhythm_data = values.get('data')
            if isinstance(rhythm_data, dict):
                # If data is a dictionary, convert notes to a simple representation
                notes = rhythm_data.get('notes', [])
                values['pattern'] = [
                    {
                        'duration': note.get('duration', 1.0),
                        'is_rest': note.get('is_rest', False)
                    } 
                    for note in notes
                ]
            elif isinstance(rhythm_data, RhythmPatternData):
                # If data is already a RhythmPatternData instance
                values['pattern'] = [
                    {
                        'duration': note.duration,
                        'is_rest': note.is_rest
                    } 
                    for note in rhythm_data.notes
                ]
        
        return values

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )


def validate_rhythm_pattern(rhythm: RhythmPattern) -> None:
    # Implementation
    pass