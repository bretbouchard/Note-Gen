"""Validation for RhythmNote models."""
from typing import List
from note_gen.core.enums import ValidationLevel
from note_gen.validation.base_validation import ValidationResult, ValidationViolation
from note_gen.models.rhythm_note import RhythmNote

class RhythmNoteValidator:
    """Validator for RhythmNote models."""
    
    @staticmethod
    def validate(note: RhythmNote, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate rhythm note based on validation level."""
        violations: List[ValidationViolation] = []
        
        # Basic validation (RELAXED)
        violations.extend(RhythmNoteValidator._validate_basic(note))
        
        if level != ValidationLevel.RELAXED:
            # NORMAL and STRICT levels
            violations.extend(RhythmNoteValidator._validate_normal(note))
            
        if level == ValidationLevel.STRICT:
            # Additional strict validations
            violations.extend(RhythmNoteValidator._validate_strict(note))
            
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @staticmethod
    def _validate_basic(note: RhythmNote) -> List[ValidationViolation]:
        """Basic validation checks."""
        violations = []
        
        # Position validation
        if note.position < 0.0:
            violations.append(ValidationViolation(
                code="invalid_position",
                message="Position cannot be negative",
                path="position"
            ))
        
        # Duration validation (allow negative for rests)
        if note.duration == 0.0:
            violations.append(ValidationViolation(
                code="invalid_duration",
                message="Duration cannot be zero",
                path="duration"
            ))
            
        return violations

    @staticmethod
    def _validate_normal(note: RhythmNote) -> List[ValidationViolation]:
        """Normal validation checks."""
        violations = []
        
        # Velocity validation (only for non-rest notes)
        if note.duration > 0 and not (0 <= note.velocity <= 127):
            violations.append(ValidationViolation(
                code="invalid_velocity",
                message="Velocity must be between 0 and 127",
                path="velocity"
            ))
        
        # Tuplet ratio validation
        numerator, denominator = note.tuplet_ratio
        if numerator <= 0 or denominator <= 0:
            violations.append(ValidationViolation(
                code="invalid_tuplet_ratio",
                message="Tuplet ratio components must be positive",
                path="tuplet_ratio"
            ))
            
        # Swing ratio validation
        if not (0.0 <= note.swing_ratio <= 1.0):
            violations.append(ValidationViolation(
                code="invalid_swing_ratio",
                message="Swing ratio must be between 0.0 and 1.0",
                path="swing_ratio"
            ))
            
        return violations

    @staticmethod
    def _validate_strict(note: RhythmNote) -> List[ValidationViolation]:
        """Strict validation checks."""
        violations = []
        
        # Humanize amount validation
        if not (0.0 <= note.humanize_amount <= 1.0):
            violations.append(ValidationViolation(
                code="invalid_humanize_amount",
                message="Humanize amount must be between 0.0 and 1.0",
                path="humanize_amount"
            ))
        
        # Groove offset validation (reasonable limits)
        if abs(note.groove_offset) > 1.0:
            violations.append(ValidationViolation(
                code="invalid_groove_offset",
                message="Groove offset should be within ±1.0 beats",
                path="groove_offset"
            ))
            
        return violations