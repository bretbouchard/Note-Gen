"""
Controller for chord progression operations.

This controller handles the business logic for chord progression operations,
including retrieving, creating, and generating chord progressions.
"""

from typing import List, Optional, Dict, Any

from note_gen.models.chord_progression import ChordProgression
from note_gen.models.chord import Chord
from note_gen.database.repositories.base import BaseRepository
from note_gen.core.enums import ChordQuality, ScaleType


class ChordProgressionController:
    """Controller for chord progression operations."""

    def __init__(self, repository: BaseRepository):
        """
        Initialize the chord progression controller.

        Args:
            repository: Repository for chord progression data access
        """
        self.repository = repository

    async def get_progression(self, progression_id: str) -> Optional[ChordProgression]:
        """
        Get a chord progression by ID.

        Args:
            progression_id: ID of the progression to retrieve

        Returns:
            The chord progression if found, None otherwise
        """
        return await self.repository.find_one(progression_id)

    async def get_all_progressions(self) -> List[ChordProgression]:
        """
        Get all chord progressions.

        Returns:
            List of all chord progressions
        """
        return await self.repository.find_many()

    async def create_progression(self, progression_data: Dict[str, Any]) -> ChordProgression:
        """
        Create a new chord progression.

        Args:
            progression_data: Data for the new progression

        Returns:
            The created chord progression
        """
        progression = ChordProgression(**progression_data)
        return await self.repository.create(progression)

    async def generate_progression(
        self, key: str, scale_type: ScaleType, complexity: float, num_chords: int
    ) -> ChordProgression:
        """
        Generate a new chord progression.

        Args:
            key: Key of the progression
            scale_type: Scale type of the progression
            complexity: Complexity factor for generation
            num_chords: Number of chords to generate

        Returns:
            The generated chord progression
        """
        # This would typically call a service or use a factory
        # For now, we'll implement a simple placeholder
        from note_gen.models.chord import Chord

        progression = ChordProgression(
            name=f"Generated {key} {scale_type} Progression",
            key=key,
            scale_type=scale_type,
            chords=[
                Chord(root="C", quality=ChordQuality.MAJOR, duration=1),
                Chord(root="F", quality=ChordQuality.MAJOR, duration=1),
                Chord(root="G", quality=ChordQuality.MAJOR, duration=1),
                Chord(root="C", quality=ChordQuality.MAJOR, duration=1),
            ][:num_chords]
        )

        return await self.repository.create(progression)
