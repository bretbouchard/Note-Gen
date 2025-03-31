"""MongoDB base repository implementation."""
from typing import TypeVar, Generic, Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class MongoDBRepository(Generic[T]):
    """Base MongoDB repository."""
    
    def __init__(self, collection: AsyncIOMotorCollection[Dict[str, Any]]) -> None:
        """Initialize MongoDB repository.
        
        Args:
            collection: MongoDB collection to use
        """
        self.collection = collection
        self._model_class: type[T]

    def _convert_to_model(self, doc: Dict[str, Any]) -> T:
        """Convert MongoDB document to model instance.
        
        Args:
            doc: MongoDB document
            
        Returns:
            Model instance
        """
        if doc is None:
            raise ValueError("Document cannot be None")
        return self._model_class(**doc)

    async def find_by_id(self, id: str) -> Optional[T]:
        """Find document by ID.
        
        Args:
            id: Document ID
            
        Returns:
            Model instance if found, None otherwise
        """
        doc = await self.collection.find_one({"_id": ObjectId(id)})
        return self._convert_to_model(doc) if doc else None

    async def find_all(self) -> List[T]:
        """Find all documents.
        
        Returns:
            List of model instances
        """
        cursor = self.collection.find()
        documents = await cursor.to_list(None)
        return [self._convert_to_model(doc) for doc in documents]

    async def insert(self, model: T) -> str:
        """Insert new document.
        
        Args:
            model: Model instance to insert
            
        Returns:
            Inserted document ID
        """
        doc = model.model_dump(exclude_unset=True)
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, id: str, model: T) -> bool:
        """Update existing document.
        
        Args:
            id: Document ID
            model: Updated model instance
            
        Returns:
            True if document was updated, False otherwise
        """
        doc = model.model_dump(exclude_unset=True)
        result = await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": doc}
        )
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        """Delete document by ID.
        
        Args:
            id: Document ID
            
        Returns:
            True if document was deleted, False otherwise
        """
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
