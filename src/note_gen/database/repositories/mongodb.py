"""MongoDB repository implementation."""
from typing import Generic, TypeVar, Dict, Any, Optional, List, Type
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class MongoDBRepository(Generic[T]):
    """Base repository for MongoDB operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str, model_class: Type[T]):
        self.database = database
        self.collection = database[collection_name]
        self.model_class = model_class

    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[T]:
        """Find single document by filter."""
        doc = await self.collection.find_one(filter_dict)
        return self._convert_to_model(doc) if doc else None

    async def find_many(self, filter_dict: Dict[str, Any]) -> List[T]:
        """Find multiple documents by filter."""
        cursor = self.collection.find(filter_dict)
        documents = await cursor.to_list(None)
        return [self._convert_to_model(doc) for doc in documents]

    def _convert_to_model(self, doc: Dict[str, Any]) -> T:
        """Convert dictionary to model instance."""
        return self.model_class.model_validate(doc)
