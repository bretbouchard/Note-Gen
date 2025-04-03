"""Factory for creating validators."""
from typing import Type, Dict, Any, Protocol, Callable, Union, List
from note_gen.core.enums import ValidationLevel
from note_gen.schemas.validation_response import ValidationResult
from note_gen.validation.pattern_validation import PatternValidator
from note_gen.validation.musical_validation import validate_note_sequence
from note_gen.models.note import Note
from note_gen.models.patterns import Pattern

class Validator(Protocol):
    """Protocol for validator classes."""
    @staticmethod
    def validate(data: Dict[str, Any], level: ValidationLevel) -> ValidationResult:
        ...

ValidatorType = Union[Type[Validator], Callable[[Dict[str, Any], ValidationLevel], ValidationResult]]

class PatternValidatorAdapter:
    """Adapter for PatternValidator to match Validator protocol."""
    @staticmethod
    def validate(data: Dict[str, Any], level: ValidationLevel) -> ValidationResult:
        pattern = Pattern(**data)
        return PatternValidator.validate(pattern, level)

class NoteSequenceValidator:
    """Adapter for note sequence validation."""
    @staticmethod
    def validate(data: Dict[str, Any], level: ValidationLevel) -> ValidationResult:
        """Adapt the note sequence validator to match the Validator protocol."""
        notes = [Note(**note_data) if isinstance(note_data, dict) else note_data 
                for note_data in data.get('notes', [])]
        return validate_note_sequence(notes, level)

class ValidationFactory:
    """Factory for creating validators."""
    
    _validators: Dict[str, ValidatorType] = {
        'NotePattern': PatternValidatorAdapter,
        'RhythmPattern': PatternValidatorAdapter,
        'ScaleInfo': NoteSequenceValidator,
    }
    
    @classmethod
    def create_validator(cls, model_type: Type) -> ValidatorType:
        """Create appropriate validator for the given model type."""
        validator = cls._validators.get(model_type.__name__)
        if not validator:
            raise ValueError(f"No validator found for model type: {model_type.__name__}")
        
        return validator

    @classmethod
    def validate(cls, model_type: Type, data: Dict[str, Any], level: ValidationLevel = ValidationLevel.NORMAL) -> ValidationResult:
        """Validate data using appropriate validator."""
        validator = cls.create_validator(model_type)
        
        if isinstance(validator, type):
            return validator.validate(data, level)
        else:
            return validator(data, level)
