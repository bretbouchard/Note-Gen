"""Custom exceptions for validation."""
from typing import Any, Dict, Optional

class ValidationError(Exception):
    """Base validation exception."""
    def __init__(
        self, 
        message: str, 
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class PatternValidationError(ValidationError):
    """Exception for pattern validation errors."""
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="PATTERN_VALIDATION_ERROR",
            details=details
        )

class NoteValidationError(ValidationError):
    """Exception for note validation errors."""
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="NOTE_VALIDATION_ERROR",
            details=details
        )

class ChordValidationError(ValidationError):
    """Exception for chord validation errors."""
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="CHORD_VALIDATION_ERROR",
            details=details
        )

class ScaleValidationError(ValidationError):
    """Exception for scale validation errors."""
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="SCALE_VALIDATION_ERROR",
            details=details
        )