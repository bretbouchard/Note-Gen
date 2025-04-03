"""
Controller for utility operations.

This controller handles utility operations such as health checks, statistics, and other
non-core functionality.
"""

from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from note_gen.core.enums import ScaleType
from note_gen.database.repositories.base import BaseRepository
from note_gen.database.repositories.chord_progression_repository import ChordProgressionRepository
from note_gen.database.repositories.note_pattern_repository import NotePatternRepository
from note_gen.database.repositories.rhythm_pattern_repository import RhythmPatternRepository
from note_gen.database.repositories.sequence_repository import SequenceRepository
from note_gen.database.repositories.user_repository import UserRepository


class UtilityController:
    """Controller for utility operations."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        chord_progression_repository: BaseRepository,
        note_pattern_repository: BaseRepository,
        rhythm_pattern_repository: BaseRepository,
        sequence_repository: BaseRepository,
        user_repository: BaseRepository
    ):
        """
        Initialize the utility controller.

        Args:
            db: The database connection
            chord_progression_repository: Repository for chord progressions
            note_pattern_repository: Repository for note patterns
            rhythm_pattern_repository: Repository for rhythm patterns
            sequence_repository: Repository for sequences
            user_repository: Repository for users
        """
        self.db = db
        self.chord_progression_repository = chord_progression_repository
        self.note_pattern_repository = note_pattern_repository
        self.rhythm_pattern_repository = rhythm_pattern_repository
        self.sequence_repository = sequence_repository
        self.user_repository = user_repository

    async def health_check(self) -> Dict[str, str]:
        """
        Perform a health check.

        Returns:
            Dict[str, str]: The health check result
        """
        return {"status": "ok"}

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the database.

        Returns:
            Dict[str, Any]: The statistics
        """
        # Get counts
        chord_progression_count = await self.db.chord_progressions.count_documents({})
        note_pattern_count = await self.db.note_patterns.count_documents({})
        rhythm_pattern_count = await self.db.rhythm_patterns.count_documents({})
        sequence_count = await self.db.sequences.count_documents({})
        user_count = await self.db.users.count_documents({})

        # Get detailed pattern information
        note_patterns_by_scale = {}
        for scale_type in ScaleType:
            count = await self.db.note_patterns.count_documents({"data.scale_type": scale_type.value})
            if count > 0:
                note_patterns_by_scale[scale_type.name] = count

        # Get chord progressions by key
        chord_progressions_by_key = {}
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        for key in keys:
            count = await self.db.chord_progressions.count_documents({"key": key})
            if count > 0:
                chord_progressions_by_key[key] = count

        # Get rhythm patterns by time signature
        rhythm_patterns_by_time_sig = {}
        time_signatures = [[4, 4], [3, 4], [6, 8], [5, 4], [7, 8]]
        for time_sig in time_signatures:
            count = await self.db.rhythm_patterns.count_documents({"time_signature": time_sig})
            if count > 0:
                rhythm_patterns_by_time_sig[f"{time_sig[0]}/{time_sig[1]}"] = count

        return {
            "statistics": {
                "chord_progressions": chord_progression_count,
                "note_patterns": note_pattern_count,
                "rhythm_patterns": rhythm_pattern_count,
                "sequences": sequence_count,
                "users": user_count
            },
            "details": {
                "note_patterns_by_scale": note_patterns_by_scale,
                "chord_progressions_by_key": chord_progressions_by_key,
                "rhythm_patterns_by_time_signature": rhythm_patterns_by_time_sig
            }
        }

    async def list_all_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all patterns.

        Returns:
            Dict[str, List[Dict[str, Any]]]: The patterns
        """
        # Get all patterns
        note_patterns = await self.note_pattern_repository.find_all()
        rhythm_patterns = await self.rhythm_pattern_repository.find_all()
        chord_progressions = await self.chord_progression_repository.find_all()

        # Convert to dictionaries
        note_pattern_dicts = [
            {
                "id": str(pattern.id),
                "name": pattern.name,
                "type": "note_pattern",
                "tags": pattern.tags
            }
            for pattern in note_patterns
        ]

        rhythm_pattern_dicts = [
            {
                "id": str(pattern.id),
                "name": pattern.name,
                "type": "rhythm_pattern",
                "tags": pattern.tags if hasattr(pattern, "tags") else []
            }
            for pattern in rhythm_patterns
        ]

        chord_progression_dicts = [
            {
                "id": str(progression.id),
                "name": progression.name,
                "type": "chord_progression",
                "key": progression.key,
                "scale_type": progression.scale_type
            }
            for progression in chord_progressions
        ]

        return {
            "note_patterns": note_pattern_dicts,
            "rhythm_patterns": rhythm_pattern_dicts,
            "chord_progressions": chord_progression_dicts
        }

    async def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information.

        Returns:
            Dict[str, Any]: The API information
        """
        return {
            "app": "Note Generator API",
            "version": "1.0.0",
            "description": "API for musical pattern generation and manipulation",
            "documentation": "/docs",
            "endpoints": [
                "/api/v1/chord-progressions",
                "/api/v1/patterns",
                "/api/v1/sequences",
                "/api/v1/users",
                "/api/v1/validation",
                "/api/v1/import-export",
                "/health",
                "/stats",
                "/patterns-list"
            ]
        }

    @classmethod
    async def create(
        cls,
        db: AsyncIOMotorDatabase,
        chord_progression_repository: BaseRepository,
        note_pattern_repository: BaseRepository,
        rhythm_pattern_repository: BaseRepository,
        sequence_repository: BaseRepository,
        user_repository: BaseRepository
    ) -> 'UtilityController':
        """
        Factory method to create a utility controller.

        Args:
            db: The database connection
            chord_progression_repository: Repository for chord progressions
            note_pattern_repository: Repository for note patterns
            rhythm_pattern_repository: Repository for rhythm patterns
            sequence_repository: Repository for sequences
            user_repository: Repository for users

        Returns:
            UtilityController: A new utility controller instance
        """
        return cls(
            db,
            chord_progression_repository,
            note_pattern_repository,
            rhythm_pattern_repository,
            sequence_repository,
            user_repository
        )
