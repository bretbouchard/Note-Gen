"""
Controller for sequence operations.

This controller handles the business logic for sequence operations,
including generating, retrieving, and manipulating sequences.
"""

from typing import List, Optional, Dict, Any, Union

from src.note_gen.database.repositories.base_repository import BaseRepository
from src.note_gen.models.sequence import Sequence
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.controllers.pattern_controller import PatternController


class SequenceController:
    """Controller for sequence operations."""

    def __init__(
        self,
        sequence_repository: BaseRepository,
        pattern_controller: PatternController,
        chord_progression_repository: BaseRepository
    ):
        """
        Initialize the sequence controller.

        Args:
            sequence_repository: Repository for sequence data access
            pattern_controller: Controller for pattern operations
            chord_progression_repository: Repository for chord progression data access
        """
        self.sequence_repository = sequence_repository
        self.pattern_controller = pattern_controller
        self.chord_progression_repository = chord_progression_repository

    async def get_sequence(self, sequence_id: str) -> Optional[Sequence]:
        """
        Get a sequence by ID.

        Args:
            sequence_id: ID of the sequence to retrieve

        Returns:
            The sequence if found, None otherwise
        """
        return await self.sequence_repository.find_by_id(sequence_id)

    async def get_all_sequences(self) -> List[Sequence]:
        """
        Get all sequences.

        Returns:
            List of all sequences
        """
        return await self.sequence_repository.find_all()

    async def create_sequence(self, sequence_data: Dict[str, Any]) -> Sequence:
        """
        Create a new sequence.

        Args:
            sequence_data: Data for the new sequence

        Returns:
            The created sequence
        """
        sequence = Sequence(**sequence_data)
        return await self.sequence_repository.create(sequence)

    async def generate_sequence(
        self,
        progression_name: str,
        pattern_name: str,
        rhythm_pattern_name: str
    ) -> NoteSequence:
        """
        Generate a sequence from a chord progression and patterns.

        Args:
            progression_name: Name of the chord progression to use
            pattern_name: Name of the note pattern to use
            rhythm_pattern_name: Name of the rhythm pattern to use

        Returns:
            The generated note sequence
        """
        # Get the chord progression
        progressions = await self.chord_progression_repository.find({"name": progression_name})
        if not progressions:
            raise ValueError(f"Chord progression not found: {progression_name}")
        progression = progressions[0]

        # Get the note pattern
        note_pattern = await self.pattern_controller.get_pattern_by_name(pattern_name, "note")
        if not note_pattern:
            raise ValueError(f"Note pattern not found: {pattern_name}")

        # Get the rhythm pattern
        rhythm_pattern = await self.pattern_controller.get_pattern_by_name(rhythm_pattern_name, "rhythm")
        if not rhythm_pattern:
            raise ValueError(f"Rhythm pattern not found: {rhythm_pattern_name}")

        # Generate the sequence
        # This would typically call a service or use a factory
        # For now, we'll implement a simple placeholder
        sequence = NoteSequence(
            name=f"Generated sequence from {progression_name}",
            notes=[],  # This would be populated with actual notes
            metadata={
                "progression_name": progression_name,
                "pattern_name": pattern_name,
                "rhythm_pattern_name": rhythm_pattern_name
            }
        )

        # Save the sequence
        return await self.sequence_repository.create(sequence)

    async def get_sequence_by_name(self, sequence_name: str) -> Optional[Sequence]:
        """
        Get a sequence by name.

        Args:
            sequence_name: Name of the sequence to retrieve

        Returns:
            The sequence if found, None otherwise
        """
        sequences = await self.sequence_repository.find({"name": sequence_name})
        return sequences[0] if sequences else None
