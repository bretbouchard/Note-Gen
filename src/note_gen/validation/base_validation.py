"""Base validation classes and types."""
from typing import List, Dict, Any, Optional, Protocol, TypeVar, Generic
from typing_extensions import Literal
from pydantic import BaseModel
from ..core.enums import ValidationLevel

# Use TypeVar with contravariant=True for input types
Input = TypeVar('Input', bound=Any, contravariant=True)

class ValidationError(BaseModel):
    """Model for validation errors."""
    field: str
    message: str
    code: str = "VALIDATION_ERROR"
    details: Dict[str, Any] = {}

class ValidationViolation(BaseModel):
    """Model for validation violations."""
    code: str
    message: str
    path: str = ""
    details: Dict[str, Any] = {}
    severity: str = "error"  # error, warning, info

class ValidationResult(BaseModel):
    """Model for validation results."""
    is_valid: bool
    errors: List[ValidationError] = []
    violations: List[ValidationViolation] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

    def add_error(self, field: str, message: str, code: str = "VALIDATION_ERROR", details: Dict[str, Any] = {}) -> None:
        """Add an error to the validation result."""
        self.errors.append(ValidationError(
            field=field,
            message=message,
            code=code,
            details=details
        ))
        self.is_valid = False

    def add_violation(self, code: str, message: str, path: str = "", details: Dict[str, Any] = {}, 
                     severity: str = "error") -> None:
        """Add a violation to the validation result."""
        self.violations.append(ValidationViolation(
            code=code,
            message=message,
            path=path,
            details=details,
            severity=severity
        ))
        if severity == "error":
            self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning to the validation result."""
        self.warnings.append(message)

    def add_detail(self, key: str, value: Any) -> None:
        """Add a detail to the validation result."""
        self.details[key] = value

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.violations.extend(other.violations)
        self.warnings.extend(other.warnings)
        self.details.update(other.details)
        self.metadata.update(other.metadata)

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0 or any(v.severity == "warning" for v in self.violations)

    @property
    def error_messages(self) -> List[str]:
        """Get all error messages."""
        return [error.message for error in self.errors] + \
               [v.message for v in self.violations if v.severity == "error"]

class BaseValidator(Protocol[Input]):
    """Base validator protocol."""
    def validate(self, data: Input, level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate data at specified level."""
        ...

    def validate_field(self, field_name: str, value: Any, 
                      level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate a single field."""
        ...

class ValidationContext:
    """Context for validation operations."""
    def __init__(self, level: ValidationLevel = ValidationLevel.NORMAL):
        self.level = level
        self.metadata: Dict[str, Any] = {}
        self.parent_path: str = ""

    def with_path(self, path: str) -> 'ValidationContext':
        """Create new context with updated path."""
        context = ValidationContext(self.level)
        context.metadata = self.metadata.copy()
        context.parent_path = f"{self.parent_path}.{path}" if self.parent_path else path
        return context

    def with_level(self, level: ValidationLevel) -> 'ValidationContext':
        """Create new context with different validation level."""
        context = ValidationContext(level)
        context.metadata = self.metadata.copy()
        context.parent_path = self.parent_path
        return context
