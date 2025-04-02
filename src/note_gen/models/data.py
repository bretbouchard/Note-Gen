"""Data models and validation for musical patterns and progressions."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from src.note_gen.core.constants import (
    RHYTHM_PATTERNS,
    NOTE_PATTERNS,
    COMMON_PROGRESSIONS,
    SCALE_INTERVALS,
    VALID_KEYS
)
from src.note_gen.core.enums import (
    ScaleType,
    ValidationLevel,
    VoiceLeadingRule
)
from src.note_gen.validation.base_validation import ValidationResult, ValidationViolation
from src.note_gen.validation.validation_manager import ValidationManager
from src.note_gen.validation.pattern_validation import validate_pattern_structure
from src.note_gen.models.base import BaseModelWithConfig

class DataStore:
    """Store for pattern data."""
    def __init__(self):
        self.patterns: Dict[str, Any] = {}

class PatternData(BaseModelWithConfig):
    """Model for pattern data."""
    name: str = Field(..., description="Pattern name")
    rhythm_pattern: str = Field(..., description="Name of rhythm pattern")
    note_pattern: str = Field(..., description="Name of note pattern")
    progression: str = Field(..., description="Name of chord progression")
    scale_type: ScaleType = Field(..., description="Scale type")
    key: str = Field(..., description="Musical key")

    def __init__(self, **data):
        """Initialize and validate pattern references."""
        super().__init__(**data)
        if self.rhythm_pattern not in RHYTHM_PATTERNS:
            raise ValueError(f"Invalid rhythm pattern: {self.rhythm_pattern}")
        if self.note_pattern not in NOTE_PATTERNS:
            raise ValueError(f"Invalid note pattern: {self.note_pattern}")
        if self.progression not in COMMON_PROGRESSIONS:
            raise ValueError(f"Invalid progression: {self.progression}")
        if self.scale_type not in SCALE_INTERVALS:
            raise ValueError(f"Invalid scale type: {self.scale_type}")
        if not any(self.key.startswith(valid_key) for valid_key in VALID_KEYS):
            raise ValueError(f"Invalid key: {self.key}")

    def validate_rhythm(self) -> ValidationResult:
        """Validate rhythm pattern."""
        pattern_data = {"pattern": self.rhythm_pattern}
        violations = validate_pattern_structure(pattern_data)
        result = ValidationResult(is_valid=not bool(violations))

        for message in violations:
            result.add_violation(
                code="RHYTHM_PATTERN_ERROR",
                message=message,
                path="rhythm_pattern"
            )

        return result

    def validate_voice_leading(self, rules: Optional[List[VoiceLeadingRule]] = None) -> ValidationResult:
        """
        Validate voice leading rules.

        Args:
            rules: Optional list of voice leading rules to check

        Returns:
            ValidationResult containing validation status and any errors
        """
        pattern_data = {
            "note_pattern": self.note_pattern,
            "progression": self.progression,
            "rules": rules or []
        }
        violations = validate_pattern_structure(pattern_data)
        result = ValidationResult(is_valid=not bool(violations))

        for message in violations:
            result.add_violation(
                code="VOICE_LEADING_ERROR",
                message=message,
                path="voice_leading"
            )

        return result

    def validate_with_rules(self, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate pattern data using validation manager.

        Args:
            level: Validation level to apply

        Returns:
            ValidationResult containing validation status and any errors
        """
        return ValidationManager.validate_model(
            self.__class__,
            self.model_dump(),
            level
        )

# Global instance for easy access
default_data_store = DataStore()

def get_data_store() -> DataStore:
    """Get the global data store instance."""
    return default_data_store
