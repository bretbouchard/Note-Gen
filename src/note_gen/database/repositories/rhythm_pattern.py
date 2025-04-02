"""Rhythm pattern repository implementation."""

from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.mongodb import MongoDBRepository
from ...models.patterns import RhythmPattern  # Updated import path

class RhythmPatternRepository(MongoDBRepository[RhythmPattern]):
    """Repository for rhythm pattern operations."""

    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str) -> None:
        """Initialize rhythm pattern repository."""
        super().__init__(database=database, collection_name=collection_name, model_class=RhythmPattern)

    async def find_by_time_signature(self, time_signature: str) -> List[RhythmPattern]:
        """Find rhythm patterns by time signature."""
        cursor = self.collection.find({"time_signature": time_signature})
        documents = await cursor.to_list(None)
        return [self._convert_to_model(doc) for doc in documents]

    # Use the parent class's _convert_to_model method
