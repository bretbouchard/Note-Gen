"""Base validation classes and types."""
from typing import List, Optional, Protocol, Dict, Any, TypeVar
from pydantic import BaseModel, Field
from src.note_gen.core.enums import ValidationLevel

Input = TypeVar('Input')

class ValidationViolation(BaseModel):
    """Represents a single validation violation."""
    field: str = Field(default="")
    message: str
    level: ValidationLevel = Field(default=ValidationLevel.NORMAL)
    code: Optional[str] = None

class ValidationResult(BaseModel):
    """Result of a validation operation."""
    is_valid: bool = Field(default=True)
    violations: List[str] = Field(default_factory=list)
    field_errors: dict[str, List[str]] = Field(default_factory=dict)

    def add_error(self, field: str, message: str) -> None:
        """Add an error message for a specific field."""
        self.is_valid = False
        if field not in self.field_errors:
            self.field_errors[field] = []
        self.field_errors[field].append(message)
        self.violations.append(f"{field}: {message}")

    def add_violation(self, message: str) -> None:
        """Add a general validation violation."""
        self.is_valid = False
        self.violations.append(message)

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
