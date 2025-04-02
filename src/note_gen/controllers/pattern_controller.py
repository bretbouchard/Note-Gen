"""
Controller for pattern operations.

This controller handles the business logic for pattern operations,
including retrieving, creating, and validating patterns.
"""

from typing import List, Optional, Dict, Any, Union

from src.note_gen.database.repositories.base_repository import BaseRepository
from src.note_gen.models.patterns import NotePattern, RhythmPattern


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

    async def get_note_pattern(self, pattern_id: str) -> Optional[NotePattern]:
        """
        Get a note pattern by ID.

        Args:
            pattern_id: ID of the pattern to retrieve

        Returns:
            The note pattern if found, None otherwise
        """
        return await self.note_pattern_repository.find_by_id(pattern_id)

    async def get_all_note_patterns(self) -> List[NotePattern]:
        """
        Get all note patterns.

        Returns:
            List of all note patterns
        """
        return await self.note_pattern_repository.find_all()

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
        return await self.rhythm_pattern_repository.find_by_id(pattern_id)

    async def get_all_rhythm_patterns(self) -> List[RhythmPattern]:
        """
        Get all rhythm patterns.

        Returns:
            List of all rhythm patterns
        """
        return await self.rhythm_pattern_repository.find_all()

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
        patterns = await repository.find({"name": pattern_name})
        return patterns[0] if patterns else None
