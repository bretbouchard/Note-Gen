"""Chord progression repository implementation."""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.database.repositories.mongodb import MongoDBRepository

class ChordProgressionRepository(MongoDBRepository[ChordProgression]):
    """Repository for chord progression operations."""

    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str) -> None:
        super().__init__(database=database, collection_name=collection_name, model_class=ChordProgression)

    async def find_by_name(self, name: str) -> Optional[ChordProgression]:
        """Find a chord progression by name."""
        doc = await self.collection.find_one({"name": name})
        return ChordProgression(**doc) if doc else None

    async def find_by_scale_type(self, scale_type: str) -> List[ChordProgression]:
        """Find chord progressions by scale type."""
        cursor = self.collection.find({"scale_type": scale_type})
        documents = await cursor.to_list(None)
        return [ChordProgression(**doc) for doc in documents]
