"""Rhythm pattern repository implementation."""

from typing import List, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorCollection
from ..repositories.mongodb import MongoDBRepository
from ...models.patterns import RhythmPattern  # Updated import path

class RhythmPatternRepository(MongoDBRepository[RhythmPattern]):
    """Repository for rhythm pattern operations."""

    def __init__(self, collection: AsyncIOMotorCollection[Dict[str, Any]]) -> None:
        """Initialize rhythm pattern repository."""
        super().__init__(collection=collection)
        self._model_class = RhythmPattern

    async def find_by_time_signature(self, time_signature: str) -> List[RhythmPattern]:
        """Find rhythm patterns by time signature."""
        cursor = self.collection.find({"time_signature": time_signature})
        documents = await cursor.to_list(None)
        return [self._convert_to_model(doc) for doc in documents]

    def _convert_to_model(self, doc: Dict[str, Any]) -> RhythmPattern:
        return RhythmPattern(**doc)
