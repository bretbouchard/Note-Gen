"""Validation pipeline for musical patterns."""
from typing import Optional
from src.note_gen.core.enums import ValidationLevel
from src.note_gen.models.patterns import NotePattern, RhythmPattern

class PatternValidationPipeline:
    """Pipeline for validating musical patterns."""
    
    def validate_note_pattern(
        self,
        pattern: NotePattern,
        level: ValidationLevel
    ) -> bool:
        """Validate a note pattern."""
        return pattern.validate_pattern(level).is_valid

    def validate_rhythm_pattern(
        self,
        pattern: RhythmPattern,
        level: ValidationLevel
    ) -> bool:
        """Validate a rhythm pattern."""
        # Add rhythm pattern validation logic here
        return True
