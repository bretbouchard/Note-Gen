"""Rhythm pattern repository implementation."""

from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from src.note_gen.models.rhythm_pattern import RhythmPattern
from .mongodb import MongoDBRepository

class RhythmPatternRepository(MongoDBRepository[RhythmPattern]):
    """Repository for rhythm pattern operations."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, RhythmPattern)

    async def find_by_time_signature(self, time_signature: str) -> List[RhythmPattern]:
        """Find rhythm patterns by time signature."""
        cursor = self.collection.find({"time_signature": time_signature})
        documents = await cursor.to_list(None)
        return [RhythmPattern(**doc) for doc in documents]

    async def find_by_duration(self, duration: int) -> List[RhythmPattern]:
        """Find patterns by total duration in beats."""
        cursor = self.collection.find({"total_duration": duration})
        documents = await cursor.to_list(None)
        return [RhythmPattern(**doc) for doc in documents]

    async def find_by_complexity(self, max_complexity: float) -> List[RhythmPattern]:
        """Find patterns with complexity less than or equal to specified value."""
        cursor = self.collection.find({"complexity": {"$lte": max_complexity}})
        documents = await cursor.to_list(None)
        return [RhythmPattern(**doc) for doc in documents]

    async def find_with_swing(self, has_swing: bool) -> List[RhythmPattern]:
        """Find patterns based on swing presence."""
        cursor = self.collection.find({"has_swing": has_swing})
        documents = await cursor.to_list(None)
        return [RhythmPattern(**doc) for doc in documents]
