"""Validation related models and utilities."""
from typing import List, Optional, Dict, Any, Protocol
from pydantic import BaseModel
from ..core.enums import ValidationLevel

class ValidationError(BaseModel):
    """Model for validation errors."""
    field: str
    message: str
    code: str = "VALIDATION_ERROR"

class ValidationViolation(BaseModel):
    """Model for validation violations."""
    code: str
    message: str
    path: str = ""
    details: Dict[str, Any] = {}

class ValidationResult(BaseModel):
    """Result of a validation operation."""
    is_valid: bool
    errors: List[ValidationError] = []
    violations: List[ValidationViolation] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

    def add_error(self, field: str, message: str, code: str = "VALIDATION_ERROR") -> None:
        """Add an error to the validation result."""
        self.errors.append(ValidationError(field=field, message=message, code=code))
        self.is_valid = False

    def add_violation(self, code: str, message: str, path: str = "", details: Dict[str, Any] = {}) -> None:
        """Add a violation to the validation result."""
        self.violations.append(ValidationViolation(
            code=code,
            message=message,
            path=path,
            details=details
        ))
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning to the validation result."""
        self.warnings.append(message)

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.violations.extend(other.violations)
        self.warnings.extend(other.warnings)
        self.details.update(other.details)
        self.metadata.update(other.metadata)

class Validator(Protocol):
    """Protocol for validators."""
    def validate(self, data: Any, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate data at specified level."""
        ...
