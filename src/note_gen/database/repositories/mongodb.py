"""MongoDB repository implementation."""
from typing import Any, Dict, List, Optional, TypeVar, Generic
from motor.motor_asyncio import AsyncIOMotorCollection
from src.note_gen.database.repositories.base import BaseRepository

T = TypeVar('T')

class MongoDBRepository(BaseRepository[T], Generic[T]):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_one(self, query: Dict[str, Any]) -> Optional[T]:
        """Find a single document."""
        result = await self.collection.find_one(query)
        return self.model_class(**result) if result else None

    async def find_many(self, query: Dict[str, Any]) -> List[T]:
        """Find multiple documents."""
        cursor = self.collection.find(query)
        results = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in results]

    async def insert_one(self, document: T) -> str:
        """Insert a single document."""
        result = await self.collection.insert_one(document.dict())
        return str(result.inserted_id)

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a single document."""
        result = await self.collection.update_one(query, {"$set": update})
        return result.modified_count > 0

    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete a single document."""
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0
