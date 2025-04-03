"""Validation for Note models."""
from typing import Dict, Any, List
import re
from note_gen.core.enums import ValidationLevel
from note_gen.core.constants import MIDI_MIN, MIDI_MAX, DEFAULTS
from note_gen.validation.base_validation import ValidationResult, ValidationViolation

ALLOWED_PITCH_REGEX = r'^[A-G]([#b])?$'

class NoteValidator:
    @staticmethod
    def validate_pitch_format(pitch: str) -> ValidationViolation | None:
        """Validate pitch format."""
        if not re.match(ALLOWED_PITCH_REGEX, pitch):
            return ValidationViolation(
                code="invalid_pitch_format",
                message=f"Invalid pitch format: {pitch}",
                path="pitch"
            )
        return None

    @staticmethod
    def validate_note_data(
        pitch: str,
        octave: int | None,
        velocity: int,
        duration: float,
        level: ValidationLevel = ValidationLevel.NORMAL
    ) -> ValidationResult:
        """Validate note data."""
        violations: List[ValidationViolation] = []
        
        # Basic validation
        if not pitch:
            violations.append(ValidationViolation(
                code="invalid_pitch",
                message="Note pitch is required",
                path="pitch"
            ))
        else:
            pitch_violation = NoteValidator.validate_pitch_format(pitch)
            if pitch_violation:
                violations.append(pitch_violation)
        
        if octave is not None and not (0 <= octave <= 8):
            violations.append(ValidationViolation(
                code="invalid_octave",
                message="Octave must be between 0 and 8",
                path="octave"
            ))
            
        if level != ValidationLevel.RELAXED:
            if not (MIDI_MIN <= velocity <= MIDI_MAX):
                violations.append(ValidationViolation(
                    code="invalid_velocity",
                    message=f"Velocity must be between {MIDI_MIN} and {MIDI_MAX}",
                    path="velocity"
                ))
            
            if duration <= 0:
                violations.append(ValidationViolation(
                    code="invalid_duration",
                    message="Duration must be positive",
                    path="duration"
                ))
                
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )




