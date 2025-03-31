"""Base validation classes and types."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ValidationViolation(BaseModel):
    """Model for validation violations."""
    code: str
    message: str
    path: str = ""
    details: Dict[str, Any] = {}

class ValidationResult(BaseModel):
    """Result of a validation operation."""
    is_valid: bool = True
    violations: List[ValidationViolation] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_error(self, field: str, message: str, code: str = "VALIDATION_ERROR") -> None:
        """Add an error message and set is_valid to False."""
        self.violations.append(ValidationViolation(
            code=code,
            message=message,
            path=field
        ))
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.is_valid = self.is_valid and other.is_valid
        self.violations.extend(other.violations)
        self.warnings.extend(other.warnings)
        self.details.update(other.details)
        self.metadata.update(other.metadata)

    def add_details(self, key: str, value: Any) -> None:
        """Add additional details to the validation result."""
        self.details[key] = value

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the validation result."""
        self.metadata[key] = value
