"""Validation response schemas."""
from src.note_gen.validation.base_validation import ValidationResult, ValidationViolation

# Re-export the types
__all__ = ['ValidationResult', 'ValidationViolation']
