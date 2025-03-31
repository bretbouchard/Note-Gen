"""Base MongoDB repository implementation."""
from typing import Generic, TypeVar, Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class MongoDBRepository(Generic[T]):
    """Base repository for MongoDB operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection[Dict[str, Any]]) -> None:
        """Initialize repository with collection."""
        self.collection = collection
        self._model_class: type[T]

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[T]:
        """Find single document by filter."""
        doc = await self.collection.find_one(filter_dict)
        return self._convert_to_model(doc) if doc else None

    async def find_many(self, filter_dict: Dict[str, Any]) -> List[T]:
        """Find multiple documents by filter."""
        cursor = self.collection.find(filter_dict)
        documents = await cursor.to_list(None)
        return [self._convert_to_model(doc) for doc in documents]

    async def create(self, model: T) -> str:
        """Create new document."""
        doc = model.model_dump(exclude_unset=True)
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, id: str, model: T) -> Optional[T]:
        """Update document by ID."""
        doc = model.model_dump(exclude_unset=True)
        result = await self.collection.find_one_and_update(
            {"_id": id},
            {"$set": doc},
            return_document=True
        )
        return self._convert_to_model(result) if result else None

    def _convert_to_model(self, doc: Dict[str, Any]) -> T:
        """Convert dictionary to model instance."""
        return self._model_class(**doc)
