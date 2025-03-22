"""Note pattern repository implementation."""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from src.note_gen.models.patterns import NotePattern
from .mongodb import MongoDBRepository

class NotePatternRepository(MongoDBRepository[NotePattern]):
    """Repository for note pattern operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        """Initialize note pattern repository.
        
        Args:
            collection: MongoDB collection for note patterns
        """
        super().__init__(collection)
        self.model_class = NotePattern

    async def find_by_pattern_type(self, pattern_type: str) -> List[NotePattern]:
        """Find note patterns by type."""
        cursor = self.collection.find({"pattern_type": pattern_type})
        documents = await cursor.to_list(None)
        return [NotePattern(**doc) for doc in documents]

    async def find_by_complexity_range(
        self, min_complexity: float, max_complexity: float
    ) -> List[NotePattern]:
        """Find note patterns within a complexity range."""
        cursor = self.collection.find({
            "complexity": {
                "$gte": min_complexity,
                "$lte": max_complexity
            }
        })
        documents = await cursor.to_list(None)
        return [NotePattern(**doc) for doc in documents]

    async def find_compatible_with_scale(self, scale_type: str) -> List[NotePattern]:
        """Find patterns compatible with a scale type."""
        cursor = self.collection.find({
            "compatible_scales": scale_type
        })
        documents = await cursor.to_list(None)
        return [NotePattern(**doc) for doc in documents]
