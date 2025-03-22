from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')

class Repository(Generic[T], ABC):
    """Abstract base class for all repositories."""
    
    @abstractmethod
    async def find_one(self, id: str) -> Optional[T]:
        """Retrieve a single document by ID."""
        pass
    
    @abstractmethod
    async def find_many(self, filter_dict: Dict[str, Any]) -> List[T]:
        """Retrieve multiple documents matching the filter."""
        pass
    
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