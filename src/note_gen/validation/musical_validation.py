"""Musical validation module."""
from typing import List, Optional, cast
from src.note_gen.core.enums import ValidationLevel
from src.note_gen.validation.base_validation import ValidationResult, ValidationViolation
from src.note_gen.models.note import Note
from src.note_gen.validation.note_validation import NoteValidator

class ValidationError(Exception):
    """Custom validation error with line information."""
    def __init__(self, message: str, line_errors: List[dict]):
        super().__init__(message)
        self.line_errors = line_errors

def validate_note_sequence(notes: List[Note], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
    """Validate a sequence of notes."""
    if not notes:
        return ValidationResult(
            is_valid=False,
            violations=[ValidationViolation(
                code="empty_sequence",
                message="Empty note sequence",
                path="notes"
            )]
        )
    
    violations: List[ValidationViolation] = []
    note_validator = NoteValidator()
    
    try:
        # Validate individual notes
        for i, note in enumerate(notes):
            result = note_validator.validate(note, level)
            if not result.is_valid:
                for violation in result.violations:
                    violation.path = f"notes[{i}].{violation.path}"
                    violations.append(violation)
        
        # Additional checks based on validation level
        if level != ValidationLevel.RELAXED:
            # Check intervals for NORMAL and STRICT levels
            for i in range(len(notes) - 1):
                current_midi = notes[i].to_midi_number()
                next_midi = notes[i + 1].to_midi_number()
                if current_midi is not None and next_midi is not None:
                    interval = abs(next_midi - current_midi)
                    
                    # Check for large intervals
                    if interval > 12:  # Octave jump
                        violations.append(ValidationViolation(
                            code="large_interval",
                            message=f"Large interval ({interval} semitones) between positions {i} and {i+1}",
                            path=f"notes[{i}]"
                        ))
        
        # Additional checks for STRICT level only
        if level == ValidationLevel.STRICT:
            violations.extend(_perform_strict_validation(notes))
            
    except Exception as e:
        line_errors = [{"line": 0, "message": str(e)}]
        raise ValidationError("Validation failed", line_errors)

    return ValidationResult(
        is_valid=len(violations) == 0,
        violations=violations
    )

def _perform_strict_validation(notes: List[Note]) -> List[ValidationViolation]:
    """Perform strict validation checks on the note sequence."""
    violations: List[ValidationViolation] = []
    
    # Check for voice leading
    for i in range(len(notes) - 2):
        if _is_parallel_motion(notes[i:i+3]):
            violations.append(ValidationViolation(
                code="parallel_motion",
                message=f"Parallel motion detected at position {i}",
                path=f"notes[{i}]"
            ))
    
    # Check for melodic contour
    if _has_excessive_repetition(notes):
        violations.append(ValidationViolation(
            code="excessive_repetition",
            message="Excessive note repetition detected",
            path="notes"
        ))
    
    return violations

def _is_parallel_motion(three_notes: List[Note]) -> bool:
    """Check for parallel motion in three consecutive notes."""
    if len(three_notes) != 3:
        return False
        
    # Use the Note class's to_midi_number() method instead of _get_midi_number
    midi_numbers = [note.to_midi_number() for note in three_notes]
    if not all(isinstance(num, int) for num in midi_numbers):
        return False
        
    # Cast the numbers to int since we've verified they are integers
    n1, n2, n3 = cast(List[int], midi_numbers)
    intervals = [n2 - n1, n3 - n2]
    
    return intervals[0] == intervals[1] and abs(intervals[0]) > 4

def _has_excessive_repetition(notes: List[Note]) -> bool:
    """Check for excessive repetition of the same note."""
    if len(notes) < 4:
        return False
        
    repetition_count = 1
    current_note = notes[0].pitch
    
    for note in notes[1:]:
        if note.pitch == current_note:
            repetition_count += 1
            if repetition_count > 3:
                return True
        else:
            repetition_count = 1
            current_note = note.pitch
            
    return False
