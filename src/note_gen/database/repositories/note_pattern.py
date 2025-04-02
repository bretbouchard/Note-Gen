"""Note pattern repository implementation."""
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..repositories.mongodb import MongoDBRepository
from ...models.patterns import NotePattern  # Updated import path

class NotePatternRepository(MongoDBRepository[NotePattern]):
    """Repository for note pattern operations."""

    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str) -> None:
        """Initialize note pattern repository."""
        super().__init__(database=database, collection_name=collection_name, model_class=NotePattern)

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
        return [self._convert_to_model(doc) for doc in documents]

    async def find_by_scale_type(self, scale_type: str) -> List[NotePattern]:
        """Find note patterns by scale type."""
        cursor = self.collection.find({"data.scale_type": scale_type})
        documents = await cursor.to_list(None)
        return [self._convert_to_model(doc) for doc in documents]

    async def find_by_validation_level(self, validation_level: str) -> List[NotePattern]:
        """Find note patterns by validation level."""
        cursor = self.collection.find({"validation_level": validation_level})
        documents = await cursor.to_list(None)
        return [self._convert_to_model(doc) for doc in documents]
