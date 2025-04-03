"""
Controller for pattern operations.

This controller handles the business logic for pattern operations,
including retrieving, creating, and validating patterns.
"""

from typing import List, Optional, Dict, Any, Union

from note_gen.database.repositories.base import BaseRepository
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern
from note_gen.core.enums import ScaleType, PatternDirection, ValidationLevel
from note_gen.models.scale_info import ScaleInfo
from note_gen.factories.pattern_factory import PatternFactory
from note_gen.validation.base_validation import ValidationResult, ValidationViolation


class PatternController:
    """Controller for pattern operations."""

    def __init__(
        self,
        note_pattern_repository: BaseRepository,
        rhythm_pattern_repository: BaseRepository
    ):
        """
        Initialize the pattern controller.

        Args:
            note_pattern_repository: Repository for note pattern data access
            rhythm_pattern_repository: Repository for rhythm pattern data access
        """
        self.note_pattern_repository = note_pattern_repository
        self.rhythm_pattern_repository = rhythm_pattern_repository
        self.pattern_factory = PatternFactory()

    async def get_note_pattern(self, pattern_id: str) -> Optional[NotePattern]:
        """
        Get a note pattern by ID.

        Args:
            pattern_id: ID of the pattern to retrieve

        Returns:
            The note pattern if found, None otherwise
        """
        return await self.note_pattern_repository.find_one(pattern_id)

    async def get_all_note_patterns(self) -> List[NotePattern]:
        """
        Get all note patterns.

        Returns:
            List of all note patterns
        """
        return await self.note_pattern_repository.find_many()

    async def create_note_pattern(self, pattern_data: Dict[str, Any]) -> NotePattern:
        """
        Create a new note pattern.

        Args:
            pattern_data: Data for the new pattern

        Returns:
            The created note pattern
        """
        pattern = NotePattern(**pattern_data)
        return await self.note_pattern_repository.create(pattern)

    async def get_rhythm_pattern(self, pattern_id: str) -> Optional[RhythmPattern]:
        """
        Get a rhythm pattern by ID.

        Args:
            pattern_id: ID of the pattern to retrieve

        Returns:
            The rhythm pattern if found, None otherwise
        """
        return await self.rhythm_pattern_repository.find_one(pattern_id)

    async def get_all_rhythm_patterns(self) -> List[RhythmPattern]:
        """
        Get all rhythm patterns.

        Returns:
            List of all rhythm patterns
        """
        return await self.rhythm_pattern_repository.find_many()

    async def create_rhythm_pattern(self, pattern_data: Dict[str, Any]) -> RhythmPattern:
        """
        Create a new rhythm pattern.

        Args:
            pattern_data: Data for the new pattern

        Returns:
            The created rhythm pattern
        """
        pattern = RhythmPattern(**pattern_data)
        return await self.rhythm_pattern_repository.create(pattern)

    async def get_pattern_by_name(
        self, pattern_name: str, pattern_type: str = "note"
    ) -> Optional[Union[NotePattern, RhythmPattern]]:
        """
        Get a pattern by name.

        Args:
            pattern_name: Name of the pattern to retrieve
            pattern_type: Type of pattern ("note" or "rhythm")

        Returns:
            The pattern if found, None otherwise
        """
        repository = (
            self.note_pattern_repository
            if pattern_type.lower() == "note"
            else self.rhythm_pattern_repository
        )

        # Find pattern by name
        patterns = await repository.find_many({"name": pattern_name})
        return patterns[0] if patterns else None

    async def generate_pattern(
        self,
        root_note: str,
        scale_type: ScaleType,
        pattern_config: Dict[str, Any]
    ) -> NotePattern:
        """
        Generate a musical pattern based on given parameters.

        Args:
            root_note: The root note (e.g. "C")
            scale_type: The scale type to use
            pattern_config: Configuration for the pattern

        Returns:
            The generated note pattern
        """
        # Extract configuration
        intervals = pattern_config.get("intervals", [0, 2, 4])

        # Create the pattern using the factory
        pattern = self.pattern_factory.create_note_pattern(
            root_note=root_note,
            scale_type=scale_type,
            intervals=intervals
        )

        # Save the pattern to the repository
        return await self.note_pattern_repository.create(pattern)

    async def validate_pattern(
        self,
        pattern: Union[NotePattern, RhythmPattern],
        validation_level: ValidationLevel = ValidationLevel.NORMAL
    ) -> ValidationResult:
        """
        Validate a pattern.

        Args:
            pattern: The pattern to validate
            validation_level: The level of validation to perform

        Returns:
            The validation result
        """
        # For now, we'll implement a simple validation
        # In a real implementation, this would use a validation service
        try:
            if isinstance(pattern, NotePattern):
                # Validate the pattern
                pattern.validate_musical_rules()
                # If we get here, validation passed
                return ValidationResult(is_valid=True)
            else:
                # For rhythm patterns, we'll just return valid for now
                return ValidationResult(is_valid=True)
        except ValueError as e:
            # If validation fails, return the error
            result = ValidationResult(is_valid=False)
            result.add_error("pattern", str(e))
            return result
