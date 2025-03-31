"""Models for musical patterns and transformations."""
from typing import TYPE_CHECKING, List, Tuple, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator, ConfigDict

# Import base classes and utilities first
from enum import Enum
from pydantic import (
    Field, 
    ConfigDict, 
    BaseModel, 
    ValidationError,
    model_validator,
    field_validator
)

# Regular imports
from .base import BaseModelWithConfig
from .note import Note
from .chord import Chord
from .scale_info import ScaleInfo
from ..core.constants import (
    DURATION_LIMITS, 
    MIDI_MIN, 
    MIDI_MAX,
    NOTE_PATTERNS,
    PATTERN_VALIDATION_LIMITS,  # Add this import
    DEFAULTS  # Add this import
)
from ..core.enums import (
    ValidationLevel, 
    ScaleType,
    PatternType,  # Make sure this is imported
    TransformationType,
    PatternDirection
)
from ..schemas.validation_response import ValidationResult, ValidationViolation
from ..validation.validation_manager import ValidationManager

# Type checking imports
if TYPE_CHECKING:
    from .rhythm_note import RhythmNote as RhythmNoteType
    from .rhythm import RhythmPattern as RhythmPatternType
else:
    RhythmNoteType = 'RhythmNote'
    RhythmPatternType = 'RhythmPattern'

class NotePatternValidationError(Exception):
    """Custom validation error for note patterns."""
    def __init__(self, message: str, violations: Optional[List[ValidationViolation]] = None) -> None:
        super().__init__(message)
        self.violations: List[ValidationViolation] = violations or []
        self.message: str = message

class NotePatternData(BaseModel):
    """Data configuration for note patterns."""
    key: str = Field(default=DEFAULTS["key"])
    root_note: str = Field(default=DEFAULTS["key"])
    scale_type: ScaleType = Field(default=ScaleType.MAJOR)
    direction: PatternDirection = Field(default=PatternDirection.UP)
    octave: int = Field(default=4)
    octave_range: Tuple[int, int] = Field(default=PATTERN_VALIDATION_LIMITS['DEFAULT_OCTAVE_RANGE'])
    max_interval_jump: int = Field(default=PATTERN_VALIDATION_LIMITS['MAX_INTERVAL_JUMP'])
    allow_chromatic: bool = Field(default=False)
    use_scale_mode: bool = Field(default=True)
    use_chord_tones: bool = Field(default=True)
    restart_on_chord: bool = Field(default=False)
    allow_parallel_motion: bool = Field(default=True)  # Added this field
    custom_interval_weights: Optional[Dict[int, float]] = None

    model_config = ConfigDict(
        validate_assignment=True,
        extra='allow'
    )

    @model_validator(mode='after')
    def validate_octave_range(self) -> 'NotePatternData':
        min_octave, max_octave = self.octave_range
        if not (PATTERN_VALIDATION_LIMITS['MIN_OCTAVE'] <= min_octave <= max_octave <= PATTERN_VALIDATION_LIMITS['MAX_OCTAVE']):
            raise ValueError(
                f"Invalid octave range: must be between {PATTERN_VALIDATION_LIMITS['MIN_OCTAVE']} "
                f"and {PATTERN_VALIDATION_LIMITS['MAX_OCTAVE']}"
            )
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    @field_validator('scale_type')
    def validate_scale_type(cls, v):
        if isinstance(v, str):
            return ScaleType(v.upper())
        return v

class Pattern(BaseModel):
    """Base class for all musical patterns."""
    model_config = ConfigDict(validate_assignment=True)
    
    id: str = Field(default="", description="Pattern ID")
    name: str = Field(
        default="",
        description="Pattern name",
        min_length=2,
        max_length=100,
        pattern=r'^[a-zA-Z][a-zA-Z0-9\s-]*$'
    )
    duration: float = Field(default=4.0, description="Pattern duration in beats")
    time_signature: Tuple[int, int] = Field(
        default=(4, 4),
        description="Time signature as (numerator, denominator)"
    )
    tags: List[str] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_pattern_base(self) -> 'Pattern':
        """Validate the pattern."""
        return self

class NotePattern(Pattern):
    """Model for note patterns."""
    model_config = ConfigDict(
        validate_assignment=False,  # Disable automatic validation on assignment
        arbitrary_types_allowed=True,
        from_attributes=True,
        validate_default=False,
    )

    name: str = Field(default="")
    pattern: List[Note] = Field(default_factory=list)
    data: Optional[NotePatternData] = None
    scale_info: Optional[ScaleInfo] = None
    skip_validation: bool = Field(default=True)

    def enable_validation(self) -> None:
        """Enable validation and run initial validation."""
        self.skip_validation = False
        self.validate_musical_rules()

    @property
    def total_duration(self) -> float:
        """Calculate total duration of the pattern."""
        total: float = 0.0
        for note in self.pattern:
            total += float(note.duration)
        return total

    def calculate_total_duration(self) -> float:
        """Calculate the total duration of all notes in the pattern."""
        return sum(float(note.duration) for note in self.pattern)

    def get_duration_as_float(self) -> float:
        """Get the pattern duration as a float."""
        return float(self.duration)

    def validate_note_range(self) -> ValidationResult:
        """Validate note range."""
        violations: List[ValidationViolation] = []
        if self.data and self.data.octave_range:
            min_octave, max_octave = self.data.octave_range
            for note in self.pattern:
                if note.octave < min_octave or note.octave > max_octave:
                    violations.append(ValidationViolation(
                        message=f"Note {note} is outside allowed octave range ({min_octave}-{max_octave})",
                        code="OCTAVE_RANGE_ERROR",
                        path="note_range"
                    ))
        return ValidationResult(is_valid=len(violations) == 0, violations=violations)

    def validate_scale_compatibility(self) -> None:
        """Validate scale compatibility."""
        if not self.scale_info:
            return
        for note in self.pattern:
            if not self.scale_info.is_note_in_scale(note):
                raise ValueError(f"Note {note} is not compatible with scale {self.scale_info}")

    def validate_voice_leading(self) -> ValidationResult:
        """Validate voice leading rules."""
        violations: List[ValidationViolation] = []
        
        if len(self.pattern) < 2:
            return ValidationResult(is_valid=True, violations=[])
        
        max_interval = self.data.max_interval_jump if self.data else PATTERN_VALIDATION_LIMITS['MAX_INTERVAL_JUMP']
        
        for i in range(len(self.pattern) - 1):
            current_note = self.pattern[i]
            next_note = self.pattern[i + 1]
            interval = abs(next_note.to_midi_number() - current_note.to_midi_number())
            
            if interval > max_interval:
                violations.append(ValidationViolation(
                    code="VALIDATION_ERROR",
                    message=f"Voice leading violation: interval {interval} exceeds maximum {max_interval}"
                ))
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    def validate_consonance(self) -> None:
        """Validate consonance rules."""
        if len(self.pattern) < 2:
            return
        for i in range(len(self.pattern) - 1):
            current_note = self.pattern[i]
            next_note = self.pattern[i + 1]
            interval = abs(next_note.to_midi_number() - current_note.to_midi_number()) % 12
            if interval not in [0, 3, 4, 7, 8, 9]:  # Consonant intervals
                raise ValueError(f"Dissonant interval {interval} between {current_note} and {next_note}")

    def validate_parallel_motion(self) -> None:
        """Validate parallel motion rules."""
        if len(self.pattern) < 3:
            return
        for i in range(len(self.pattern) - 2):
            if self._is_parallel_motion(self.pattern[i:i+3]):
                raise ValueError(f"Parallel motion detected at position {i}")

    @staticmethod
    def validate_pattern_structure(data: Dict[str, Any]) -> List[ValidationViolation]:
        """Validate the basic structure of a pattern."""
        violations: List[ValidationViolation] = []
        
        required_fields = {'name', 'pattern', 'data'}
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            violations.append(ValidationViolation(
                message=f"Missing required fields: {', '.join(missing_fields)}",
                code="MISSING_FIELDS"
            ))
            
        if 'pattern' in data and not isinstance(data['pattern'], list):
            violations.append(ValidationViolation(
                message="Pattern must be a list",
                code="INVALID_PATTERN_TYPE"
            ))
            
        if 'data' in data and not isinstance(data['data'], dict):
            violations.append(ValidationViolation(
                message="Data must be a dictionary",
                code="INVALID_DATA_TYPE"
            ))
            
        return violations

    def validate_pattern(self, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate the entire pattern."""
        violations: List[ValidationViolation] = []
        
        try:
            # Basic validation
            if not self.pattern:
                violations.append(ValidationViolation(
                    message="Pattern cannot be empty",
                    code="EMPTY_PATTERN",
                    path="pattern"
                ))
                return ValidationResult(is_valid=False, violations=violations)

            # Scale compatibility
            if self.scale_info:
                try:
                    self.validate_scale_compatibility()
                except ValueError as e:
                    violations.append(ValidationViolation(
                        message=str(e),
                        code="SCALE_COMPATIBILITY_ERROR",
                        path="scale_compatibility"
                    ))

            # Voice leading
            if level >= ValidationLevel.NORMAL:
                try:
                    self.validate_voice_leading()
                except ValueError as e:
                    violations.append(ValidationViolation(
                        message=str(e),
                        code="VOICE_LEADING_ERROR",
                        path="voice_leading"
                    ))

            # Strict validation
            if level == ValidationLevel.STRICT:
                try:
                    self.validate_consonance()
                    self.validate_parallel_motion()
                except ValueError as e:
                    violations.append(ValidationViolation(
                        message=str(e),
                        code="STRICT_VALIDATION_ERROR",
                        path="strict_validation"
                    ))

        except Exception as e:
            violations.append(ValidationViolation(
                message=str(e),
                code="VALIDATION_ERROR",
                path="pattern",
                details={"exception_type": type(e).__name__}
            ))

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @classmethod
    def validate_pattern_data(cls, data: Dict[str, Any]) -> ValidationResult:
        """Validate pattern data."""
        try:
            # Convert the data dict to NotePatternData
            if 'data' in data:
                data['data'] = NotePatternData(**data['data'])
            
            # Convert pattern items to Note objects if they're dicts
            if 'pattern' in data and isinstance(data['pattern'], list):
                data['pattern'] = [
                    Note(**note) if isinstance(note, dict) else note
                    for note in data['pattern']
                ]

            # Create and validate the pattern
            pattern = cls(**data)
            
            # Perform all validations
            pattern.validate_scale_compatibility()
            pattern.validate_voice_leading()
            pattern.validate_consonance()
            pattern.validate_parallel_motion()

            return ValidationResult(is_valid=True)
        except (ValidationError, ValueError, AttributeError) as e:
            return ValidationResult(
                is_valid=False,
                violations=[
                    ValidationViolation(
                        code='VALIDATION_ERROR',
                        message=str(e),
                        details={'exception_type': type(e).__name__}
                    )
                ]
            )

    @model_validator(mode='after')
    def validate_musical_rules(self) -> 'NotePattern':
        """Validate musical rules for the pattern."""
        if self.skip_validation:
            return self
            
        errors: List[Dict[str, Any]] = []

        try:
            # Scale compatibility check
            if self.scale_info and not (self.data and self.data.allow_chromatic):
                for note in self.pattern:
                    if not self.scale_info.is_note_in_scale(note):
                        errors.append({
                            'loc': ('pattern',),
                            'msg': f"Note {note.pitch}{note.octave} is not compatible with scale {self.scale_info.key} {self.scale_info.scale_type}",
                            'type': 'value_error',
                            'ctx': {'error': 'scale_compatibility'}
                        })

            # Voice leading check
            if len(self.pattern) >= 2:
                for i in range(len(self.pattern) - 1):
                    current_note = self.pattern[i]
                    next_note = self.pattern[i + 1]
                    interval = abs(next_note.to_midi_number() - current_note.to_midi_number())
                    if self.data and interval > self.data.max_interval_jump:
                        errors.append({
                            'loc': ('pattern',),
                            'msg': f"Voice leading violation: interval {interval} exceeds maximum {self.data.max_interval_jump}",
                            'type': 'value_error',
                            'ctx': {'error': 'voice_leading'}
                        })

            # Parallel motion check
            if self.data and not self.data.allow_parallel_motion and len(self.pattern) >= 3:
                for i in range(len(self.pattern) - 2):
                    if self._is_parallel_motion(self.pattern[i:i+3]):
                        errors.append({
                            'loc': ('pattern',),
                            'msg': f"Parallel motion detected at position {i}",
                            'type': 'value_error',
                            'ctx': {'error': 'parallel_motion'}
                        })

            # Consonance check
            if len(self.pattern) >= 2:
                for i in range(len(self.pattern) - 1):
                    current_note = self.pattern[i]
                    next_note = self.pattern[i + 1]
                    interval = abs(next_note.to_midi_number() - current_note.to_midi_number()) % 12
                    if interval not in [0, 3, 4, 7, 8, 9]:  # Consonant intervals
                        errors.append({
                            'loc': ('pattern',),
                            'msg': f"Dissonant interval {interval} between {current_note} and {next_note}",
                            'type': 'value_error',
                            'ctx': {'error': 'consonance'}
                        })

        except Exception as e:
            errors.append({
                'loc': ('pattern',),
                'msg': str(e),
                'type': 'value_error',
                'ctx': {'error': 'validation_error'}
            })

        if errors:
            raise ValidationError.from_exception_data(
                title='Musical Rule Validation Error',
                line_errors=errors
            )

        return self

    def _is_parallel_motion(self, notes: List[Note]) -> bool:
        """Check if three consecutive notes form parallel motion."""
        if len(notes) < 3:
            return False
        
        # Calculate intervals between consecutive notes
        intervals = [
            notes[i + 1].to_midi_number() - notes[i].to_midi_number()
            for i in range(len(notes) - 1)
        ]
        
        # Check if intervals are the same and in the same direction
        return (intervals[0] == intervals[1] and 
                ((intervals[0] > 0 and intervals[1] > 0) or 
                 (intervals[0] < 0 and intervals[1] < 0)))

    def check_musical_rules(self, 
                          validate_consonance: bool = True, 
                          validate_parallel: bool = True,
                          validate_scale: bool = True) -> ValidationResult:
        """Check musical rules for the pattern."""
        violations: List[ValidationViolation] = []

        if not self.pattern:
            return ValidationResult(is_valid=True, violations=[])

        try:
            # Scale compatibility check
            if validate_scale and self.scale_info and not (self.data and self.data.allow_chromatic):
                for note in self.pattern:
                    if not self.scale_info.is_note_in_scale(note):
                        violations.append(ValidationViolation(
                            code="SCALE_COMPATIBILITY_ERROR",
                            message=f"Note {note.pitch}{note.octave} is not compatible with scale {self.scale_info.key} {self.scale_info.scale_type}"
                        ))

            # Parallel motion check
            if validate_parallel and self.data and not self.data.allow_parallel_motion:
                for i in range(len(self.pattern) - 2):
                    if self._is_parallel_motion(self.pattern[i:i+3]):
                        violations.append(ValidationViolation(
                            code="PARALLEL_MOTION_ERROR",
                            message=f"Parallel motion detected at position {i}"
                        ))

            # Consonance check
            if validate_consonance and len(self.pattern) >= 2:
                for i in range(len(self.pattern) - 1):
                    current_note = self.pattern[i]
                    next_note = self.pattern[i + 1]
                    interval = abs(next_note.to_midi_number() - current_note.to_midi_number()) % 12
                    if interval not in [0, 3, 4, 7, 8, 9]:  # Consonant intervals
                        violations.append(ValidationViolation(
                            code="CONSONANCE_ERROR",
                            message=f"Dissonant interval {interval} between {current_note.pitch}{current_note.octave} and {next_note.pitch}{next_note.octave}"
                        ))

        except Exception as e:
            violations.append(ValidationViolation(
                code="VALIDATION_ERROR",
                message=str(e)
            ))

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @model_validator(mode='after')
    def validate_all_rules(self) -> 'NotePattern':
        """Validate all musical rules."""
        # Skip validation during initial creation
        if not self.pattern or getattr(self, '_skip_validation', False):
            return self
        try:
            # Only perform basic validation during initialization
            return self
        except ValueError as e:
            raise ValueError(f"Basic validation error: {str(e)}")

    @model_validator(mode='after')
    def validate_data_requirements(self) -> 'NotePattern':
        """Validate required data fields."""
        if not self.data or not hasattr(self.data, 'scale_type'):
            from pydantic import ValidationError
            raise ValueError('Field required: scale_type')  # Simpler approach
            # Or use the more detailed approach:
            # errors = [
            #     {
            #         'type': 'value_error.missing',
            #         'loc': ('data', 'scale_type'),
            #         'msg': 'Field required: scale_type',
            #         'input': None,
            #     }
            # ]
            # raise ValueError(f"Validation error: {errors}")
        return self

    @model_validator(mode='after')
    def validate_pattern_timing(self) -> 'NotePattern':
        """Validate pattern timing."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")
        return self

    @field_validator('pattern')
    @classmethod
    def validate_pattern_contents(cls, v: List[Note]) -> List[Note]:
        """Validate pattern contents."""
        if not v:
            return v
        if not all(isinstance(note, Note) for note in v):
            raise ValueError("Pattern must contain only Note objects")
        return v

    def validate_all(self) -> ValidationResult:
        """Perform all validations after initialization."""
        violations: List[ValidationViolation] = []
        
        try:
            # Validate note range first
            range_result = self.validate_note_range()
            if not range_result.is_valid:
                violations.extend(range_result.violations)
                # Return early if range validation fails
                return ValidationResult(
                    is_valid=False,
                    violations=violations
                )

            # Only proceed with other validations if range check passes
            if self.scale_info:
                self.validate_scale_compatibility()
            if self.data:
                self.validate_voice_leading()
            
        except ValueError as e:
            violations.append(
                ValidationViolation(
                    code="VALIDATION_ERROR",
                    message=str(e)
                )
            )
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @classmethod
    def from_preset(cls, preset_name: str, **kwargs: Any) -> 'NotePattern':
        """
        Create a pattern from a preset configuration.

        Args:
            preset_name: Name of the preset from NOTE_PATTERNS
            **kwargs: Additional arguments to override preset values

        Returns:
            NotePattern instance configured according to the preset

        Raises:
            ValueError: If preset_name is not found in NOTE_PATTERNS
        """
        if preset_name not in NOTE_PATTERNS:
            raise ValueError(f"Preset '{preset_name}' not found in NOTE_PATTERNS")

        # Get the preset data
        preset_data = dict(NOTE_PATTERNS[preset_name])

        # Create pattern data
        pattern_data = {
            'intervals': preset_data.get('intervals', []),
            'direction': preset_data.get('direction', PatternDirection.UP),
            'scale_type': preset_data.get('scale_type', ScaleType.MAJOR)
        }

        # Create NotePatternData instance
        note_pattern_data = NotePatternData(**pattern_data)

        # Create initial pattern with at least one note
        pattern = [
            Note(
                pitch='C',  # Changed from note_name to pitch
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=100
            )
        ]

        # Create and return the NotePattern
        return cls(
            name=preset_name,
            pattern=pattern,
            data=note_pattern_data
        )

    @classmethod
    def from_pattern(cls, pattern: List[int], root_note: str = "C4", **kwargs: Any) -> 'NotePattern':
        """Create a pattern from a list of intervals."""
        root = Note.from_name(root_note)
        if root is None:
            raise ValueError(f"Invalid root note: {root_note}")
            
        notes: List[Note] = []
        for interval in pattern:
            midi_num = root.to_midi_number() + interval
            note = Note.from_midi_number(midi_num)
            if note is not None:
                notes.append(note)
        
        pattern_data = NotePatternData(
            key=root_note,
            root_note=root.pitch,
            intervals=pattern,
            **kwargs  # Allow additional fields to be set
        )
        
        return cls(
            pattern=notes,
            data=pattern_data
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotePattern':
        """Create a pattern from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary")
            
        pattern_data = NotePatternData(**data.get('data', {}))
        notes = [Note(**note_data) for note_data in data.get('pattern', [])]
        
        return cls(
            name=data.get('name', ''),
            pattern=notes,
            data=pattern_data
        )

class RhythmNote(BaseModel):
    """Model representing a rhythmic note."""
    position: float = Field(ge=0.0, description="Position in beats from start")
    duration: float = Field(gt=0.0, description="Duration in beats")
    velocity: float = Field(default=64.0, ge=0.0, le=127.0, description="MIDI velocity")  # Changed to float
    accent: bool = Field(default=False, description="Whether the note is accented")

    def get_velocity_int(self) -> int:
        """Get the note velocity as integer."""
        return int(self.velocity)

    def get_duration(self) -> float:
        """Get the note duration."""
        return self.duration

class RhythmPatternData(BaseModel):
    """Data configuration for rhythm patterns."""
    time_signature: Tuple[int, int] = Field(
        default=(4, 4),
        description="Time signature as (numerator, denominator)"
    )
    notes: List[RhythmNote] = Field(
        default_factory=list,
        description="List of rhythm notes"
    )
    subdivision: str = Field(
        default="quarter",
        description="Base subdivision type"
    )
    swing_enabled: bool = Field(default=False)
    humanize_amount: float = Field(default=0.0)
    swing_ratio: float = Field(default=0.67)
    default_duration: float = Field(default=1.0)
    total_duration: float = Field(default=4.0)
    accent_pattern: List[bool] = Field(default_factory=list)
    groove_type: str = Field(default="straight")
    variation_probability: float = Field(default=0.1)
    duration: float = Field(default=4.0)
    style: str = Field(default="basic")

class RhythmPattern(BaseModelWithConfig):
    """Model for rhythm patterns."""
    
    pattern: List[RhythmNote] = Field(
        default_factory=list,
        description="List of rhythm notes"
    )
    time_signature: Tuple[int, int] = Field(default=(4, 4))
    swing_enabled: bool = Field(default=False)
    humanize_enabled: bool = Field(default=False)
    swing_ratio: float = Field(
        default=0.67,
        ge=0.5,
        le=0.75,
        description="Swing ratio (0.5-0.75)"
    )
    humanize_amount: float = Field(
        default=0.0,
        ge=0.0,
        le=0.1,
        description="Humanization amount (0.0-0.1)"
    )
    
    @model_validator(mode='after')
    def validate_pattern(self) -> 'RhythmPattern':
        """Validate the rhythm pattern."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")
            
        # Validate time signature denominator (must be power of 2)
        if self.time_signature[1] not in [1, 2, 4, 8, 16, 32, 64]:
            raise ValueError("Time signature denominator must be a power of 2")
            
        # Check if notes are ordered by position
        positions = [note.position for note in self.pattern]
        if positions != sorted(positions):
            raise ValueError("Notes must be ordered by position")
            
        return self

class ChordProgressionPattern(Pattern):
    """Model for chord progression patterns."""
    model_config = ConfigDict(validate_assignment=True)

    chords: List[Chord] = Field(
        default_factory=list,
        description="List of chords in the progression"
    )
    scale_type: str = Field(  # Changed from ScaleType to str since ScaleType wasn't defined
        default="major",
        description="Scale type for the progression"
    )
    root_note: str = Field(
        default="C",
        description="Root note of the progression"
    )

    @field_validator('chords')
    @classmethod
    def validate_chord_sequence(cls, v: List[Chord]) -> List[Chord]:
        """Validate the chord sequence."""
        if not v:
            raise ValueError("Chord progression must contain at least one chord")
        return v

class TransformationModel(BaseModel):
    """Model for pattern transformations."""
    type: str
    parameters: Optional[Dict[str, Any]] = None
