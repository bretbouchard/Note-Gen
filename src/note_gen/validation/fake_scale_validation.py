"""Validation for FakeScaleInfo model used in testing."""
from typing import Dict, Any, List
from note_gen.core.enums import ValidationLevel, ScaleType
from note_gen.core.constants import VALID_KEYS
from note_gen.schemas.validation_response import ValidationResult
from note_gen.core.accessors import NoteAccessor

class FakeScaleValidator:
    @staticmethod
    def validate(data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate fake scale data based on validation level."""
        violations = []
        
        violations.extend(FakeScaleValidator._validate_basic(data))
        
        if level >= ValidationLevel.NORMAL:
            violations.extend(FakeScaleValidator._validate_normal(data))
            
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations
        )

    @staticmethod
    def _validate_basic(data: Dict[str, Any]) -> List[str]:
        """Basic validation checks."""
        violations = []
        
        # Validate key
        key = data.get('key')
        if not key or not isinstance(key, str):
            violations.append("Key is required and must be a string")
        elif not NoteAccessor.validate_note_name(key):
            violations.append(f"Invalid key format: {key}")
            
        # Validate scale type
        scale_type = data.get('scale_type')
        if not isinstance(scale_type, ScaleType):
            violations.append("Invalid scale type")
            
        return violations

    @staticmethod
    def _validate_normal(data: Dict[str, Any]) -> List[str]:
        """Normal validation checks."""
        violations = []
        
        # Validate complexity
        complexity = data.get('complexity', 0.5)
        if not isinstance(complexity, (int, float)) or not (0 <= complexity <= 1):
            violations.append("Complexity must be a number between 0 and 1")
            
        return violations