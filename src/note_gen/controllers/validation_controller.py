"""
Controller for validation operations.

This controller centralizes validation logic for all models in the application.
It provides methods to validate different types of models and structures.
"""

from typing import Dict, Any, Type, List, Union, Optional
from pydantic import BaseModel

from note_gen.core.enums import ValidationLevel
from note_gen.validation.base_validation import ValidationResult, ValidationViolation
from note_gen.validation.validation_manager import ValidationManager
from note_gen.validation.validation_factory import ValidationFactory
from note_gen.models.patterns import NotePattern, Pattern
from note_gen.models.rhythm import RhythmPattern
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.note import Note


class ValidationController:
    """Controller for validation operations."""

    def __init__(self):
        """Initialize the validation controller."""
        self.validation_manager = ValidationManager()

    async def validate_model(self, model: Any, level: Optional[ValidationLevel] = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate a model instance.

        Args:
            model: The model instance to validate
            level: The validation level to apply

        Returns:
            ValidationResult: The validation result
        """
        # Use default level if None is provided
        validation_level = level if level is not None else ValidationLevel.NORMAL

        if hasattr(model, 'model_validate'):
            return model.model_validate(validation_level)
        elif hasattr(model, 'validate'):  # For backward compatibility
            return model.validate(validation_level)
        return self.validation_manager.validate(model)

    async def validate_note_pattern(self, pattern: Union[Dict[str, Any], NotePattern],
                              level: Optional[ValidationLevel] = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate a note pattern.

        Args:
            pattern: The note pattern to validate
            level: The validation level to apply

        Returns:
            ValidationResult: The validation result
        """
        if isinstance(pattern, dict):
            try:
                pattern = NotePattern.model_validate(pattern)
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    violations=[ValidationViolation(
                        message=f"Invalid note pattern format: {str(e)}",
                        code="VALIDATION_ERROR"
                    )]
                )

        return await self.validate_model(pattern, level)

    async def validate_rhythm_pattern(self, pattern: Union[Dict[str, Any], RhythmPattern],
                                level: Optional[ValidationLevel] = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate a rhythm pattern.

        Args:
            pattern: The rhythm pattern to validate
            level: The validation level to apply

        Returns:
            ValidationResult: The validation result
        """
        if isinstance(pattern, dict):
            try:
                pattern = RhythmPattern.model_validate(pattern)
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    violations=[ValidationViolation(
                        message=f"Invalid rhythm pattern format: {str(e)}",
                        code="VALIDATION_ERROR"
                    )]
                )

        return await self.validate_model(pattern, level)

    async def validate_note_sequence(self, sequence: Union[Dict[str, Any], NoteSequence],
                               level: Optional[ValidationLevel] = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate a note sequence.

        Args:
            sequence: The note sequence to validate
            level: The validation level to apply

        Returns:
            ValidationResult: The validation result
        """
        if isinstance(sequence, dict):
            try:
                sequence = NoteSequence.model_validate(sequence)
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    violations=[ValidationViolation(
                        message=f"Invalid note sequence format: {str(e)}",
                        code="VALIDATION_ERROR"
                    )]
                )

        return await self.validate_model(sequence, level)

    async def validate_chord_progression(self, progression: Union[Dict[str, Any], ChordProgression],
                                   level: Optional[ValidationLevel] = ValidationLevel.NORMAL) -> ValidationResult:
        """
        Validate a chord progression.

        Args:
            progression: The chord progression to validate
            level: The validation level to apply

        Returns:
            ValidationResult: The validation result
        """
        if isinstance(progression, dict):
            try:
                progression = ChordProgression.model_validate(progression)
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    violations=[ValidationViolation(
                        message=f"Invalid chord progression format: {str(e)}",
                        code="VALIDATION_ERROR"
                    )]
                )

        return await self.validate_model(progression, level)

    async def validate_config(self, config: Dict[str, Any], config_type: str) -> bool:
        """
        Validate a configuration dictionary.

        Args:
            config: The configuration to validate
            config_type: The type of configuration

        Returns:
            bool: True if valid, False otherwise
        """
        return self.validation_manager.validate_config(config, config_type)

    @classmethod
    async def create(cls) -> 'ValidationController':
        """
        Factory method to create a validation controller.

        Returns:
            ValidationController: A new validation controller instance
        """
        return cls()
