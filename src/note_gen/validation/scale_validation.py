"""Scale validation module."""
from typing import List, Tuple, Optional, Dict, Any
from src.note_gen.core.constants import (
    SCALE_INTERVALS,
    ScaleValidator,
    FULL_NOTE_REGEX
)
from src.note_gen.core.enums import ScaleType, ValidationLevel
from src.note_gen.validation.base_validation import ValidationResult, ValidationViolation
from src.note_gen.validation.note_validator import NoteValidator
from src.note_gen.models.scale import Scale, ScaleInfo
from src.note_gen.models.note import Note

class ScaleValidation:
    """Scale validation class."""
    
    @staticmethod
    def validate_scale(scale: Scale, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate a Scale instance.
        
        Args:
            scale: The Scale instance to validate
            level: Validation level to apply
            
        Returns:
            ValidationResult indicating if the scale is valid
        """
        violations: List[ValidationViolation] = []
        note_validator = NoteValidator()
        
        # Validate root note
        if not scale.root:
            violations.append(
                ValidationViolation(
                    code="MISSING_ROOT",
                    message="Scale must have a root note",
                    path="root"
                )
            )
        elif isinstance(scale.root, Note):
            root_result = note_validator.validate(scale.root, level)
            if not root_result.is_valid:
                for violation in root_result.violations:
                    violation.path = f"root.{violation.path}"
                    violations.append(violation)
        else:
            violations.append(
                ValidationViolation(
                    code="INVALID_ROOT",
                    message="Root must be a valid Note instance",
                    path="root"
                )
            )

        # Validate scale type and intervals
        type_result = ScaleValidation.validate_scale_type(scale.scale_type, scale.notes)
        violations.extend(type_result.violations)
        
        # Validate octave range
        if not (0 <= scale.octave_range[0] <= scale.octave_range[1] <= 8):
            violations.append(
                ValidationViolation(
                    code="INVALID_OCTAVE_RANGE",
                    message="Invalid octave range",
                    path="octave_range",
                    details={"range": scale.octave_range}
                )
            )

        # Validate generated notes
        if scale.notes:
            for i, note in enumerate(scale.notes):
                if isinstance(note, Note):
                    note_result = note_validator.validate(note, level)
                    if not note_result.is_valid:
                        for violation in note_result.violations:
                            violation.path = f"notes[{i}].{violation.path}"
                            violations.append(violation)
                else:
                    violations.append(
                        ValidationViolation(
                            code="INVALID_NOTE",
                            message=f"Invalid note at position {i}",
                            path=f"notes[{i}]"
                        )
                    )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @staticmethod
    def validate_scale_info(scale_info: ScaleInfo, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate a ScaleInfo instance.
        
        Args:
            scale_info: The ScaleInfo instance to validate
            level: Validation level to apply
            
        Returns:
            ValidationResult indicating if the scale info is valid
        """
        violations: List[ValidationViolation] = []
        
        # Validate key format using the imported regex pattern
        if not FULL_NOTE_REGEX.match(scale_info.key):
            violations.append(
                ValidationViolation(
                    code="INVALID_KEY_FORMAT",
                    message=f"Invalid key format: {scale_info.key}",
                    path="key"
                )
            )
        
        # Validate root note
        try:
            root_note = Note.from_name(scale_info.key)
            note_validator = NoteValidator()
            root_result = note_validator.validate(root_note, level)
            if not root_result.is_valid:
                for violation in root_result.violations:
                    violation.path = f"key.{violation.path}"
                    violations.append(violation)
        except ValueError as e:
            violations.append(
                ValidationViolation(
                    code="INVALID_ROOT_NOTE",
                    message=str(e),
                    path="key"
                )
            )

        # Validate scale type
        if scale_info.scale_type not in SCALE_INTERVALS:
            violations.append(
                ValidationViolation(
                    code="INVALID_SCALE_TYPE",
                    message=f"Invalid scale type: {scale_info.scale_type}",
                    path="scale_type"
                )
            )

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @staticmethod
    def validate_scale_type(scale_type: ScaleType, notes: Optional[List[Note]] = None) -> ValidationResult:
        """
        Validate a scale type and optionally its notes.
        
        Args:
            scale_type: The type of scale to validate
            notes: Optional list of notes to validate against the scale type
            
        Returns:
            ValidationResult indicating if the scale type is valid
        """
        violations: List[ValidationViolation] = []
        
        # Validate scale type exists
        if scale_type not in SCALE_INTERVALS:
            violations.append(
                ValidationViolation(
                    code="INVALID_SCALE_TYPE",
                    message=f"Invalid scale type: {scale_type}",
                    path="scale_type"
                )
            )
            return ValidationResult(
                is_valid=False,
                violations=violations
            )
        
        # If notes provided, validate against scale intervals
        if notes and len(notes) > 0:
            expected_intervals = SCALE_INTERVALS[scale_type]
            root_midi = notes[0].to_midi_number()  # Use to_midi_number() method
            actual_intervals = tuple(
                note.to_midi_number() - root_midi for note in notes  # Use to_midi_number() method
            )
            
            if not ScaleValidator.validate_intervals(actual_intervals):
                violations.append(
                    ValidationViolation(
                        code="INVALID_INTERVALS",
                        message="Invalid interval sequence",
                        path="notes",
                        details={"intervals": actual_intervals}
                    )
                )
            
            if actual_intervals != expected_intervals:
                violations.append(
                    ValidationViolation(
                        code="INTERVAL_MISMATCH",
                        message=f"Intervals do not match {scale_type} scale pattern",
                        path="notes",
                        details={
                            "expected": expected_intervals,
                            "actual": actual_intervals
                        }
                    )
                )
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )
