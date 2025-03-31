"""Base repository pattern implementation."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Abstract base repository."""
    
    def __init__(self, collection: AsyncIOMotorCollection[Any]) -> None:
        self.collection = collection

    @abstractmethod
    async def find_one(self, id: str) -> Optional[T]:
        """Find a single document by ID."""
        pass

    @abstractmethod
    async def find_many(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[T]:
        """Find multiple documents matching filter criteria."""
        # Use empty dict as default filter to match all documents
        actual_filter = filter_dict if filter_dict is not None else {}
        cursor = self.collection.find(actual_filter)
        documents = await cursor.to_list(length=None)
        return [self._convert_to_model(doc) for doc in documents]

    @abstractmethod
    async def create(self, document: T) -> T:
        """Create a new document."""
        pass

    @abstractmethod
    async def update(self, id: str, document: T) -> Optional[T]:
        """Update an existing document."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        pass

    @abstractmethod
    def _convert_to_model(self, data: Dict[str, Any]) -> T:
        """Convert dictionary data to model instance."""
        pass
