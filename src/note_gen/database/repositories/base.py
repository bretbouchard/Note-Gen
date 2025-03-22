"""Base repository pattern implementation."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for database operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    @abstractmethod
    async def create(self, item: T) -> str:
        """Create a new item."""
        pass

    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """Get an item by ID."""
        pass

    @abstractmethod
    async def get_all(self, filter_dict: Dict[str, Any] = None) -> List[T]:
        """Get all items matching the filter."""
        pass

    @abstractmethod
    async def update(self, id: str, item: T) -> bool:
        """Update an item."""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an item."""
        pass

    @abstractmethod
    async def exists(self, id: str) -> bool:
        """Check if an item exists."""
        pass