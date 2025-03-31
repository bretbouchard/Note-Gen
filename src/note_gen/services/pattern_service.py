"""Service for pattern-related operations."""
import re
from typing import Dict, Any, Union
from src.note_gen.core.enums import ScaleType, ValidationLevel
from src.note_gen.models.patterns import NotePattern, NotePatternData, RhythmPattern
from src.note_gen.validation.validation_manager import ValidationManager
from src.note_gen.validation.base_validation import ValidationResult, ValidationViolation

# Define a Pattern type that can be either NotePattern or RhythmPattern
PatternType = Union[NotePattern, RhythmPattern]

class PatternService:
    """Service for handling pattern operations."""
    
    async def generate_musical_pattern(
        self,
        root_note: str,
        scale_type: ScaleType,
        pattern_config: Dict[str, Any]
    ) -> NotePattern:
        """Generate a musical pattern based on given parameters."""
        if not re.match(r'^[A-G][#b]?$', root_note):
            raise ValueError(f"Invalid root note format: {root_note}")

        pattern_data = NotePatternData(
            root_note=root_note,
            scale_type=scale_type,
            **pattern_config
        )

        pattern = NotePattern(
            name=f"{root_note} {scale_type.value} Pattern",
            data=pattern_data
        )

        validation_result = pattern.validate_pattern(ValidationLevel.NORMAL)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid pattern: {[v.message for v in validation_result.violations]}")

        return pattern

    async def validate_pattern(self, pattern: PatternType) -> ValidationResult:
        """Validate a pattern."""
        return ValidationResult(
            is_valid=True,
            violations=[]
        )
