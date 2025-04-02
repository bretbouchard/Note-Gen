"""Rhythm pattern repository implementation for the MCP architecture."""
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from note_gen.database.repositories.mongodb_repository import MongoDBRepository
from note_gen.models.patterns import RhythmPattern

class RhythmPatternRepository(MongoDBRepository[RhythmPattern]):
    """Repository for rhythm pattern operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """
        Initialize the rhythm pattern repository.
        
        Args:
            collection: MongoDB collection to use
        """
        super().__init__(collection, RhythmPattern)

    async def find_by_name(self, name: str) -> Optional[RhythmPattern]:
        """
        Find a rhythm pattern by name.
        
        Args:
            name: Name of the rhythm pattern
            
        Returns:
            RhythmPattern if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"name": name})
            return self._convert_to_model(doc) if doc else None
        except Exception as e:
            # Log the error
            print(f"Error finding rhythm pattern by name: {e}")
            return None

    async def find_by_time_signature(self, time_signature: Tuple[int, int]) -> List[RhythmPattern]:
        """
        Find rhythm patterns by time signature.
        
        Args:
            time_signature: Time signature as (numerator, denominator)
            
        Returns:
            List of RhythmPattern instances
        """
        try:
            cursor = self.collection.find({"time_signature": list(time_signature)})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding rhythm patterns by time signature: {e}")
            return []

    async def find_by_style(self, style: str) -> List[RhythmPattern]:
        """
        Find rhythm patterns by style.
        
        Args:
            style: Style of the rhythm pattern
            
        Returns:
            List of RhythmPattern instances
        """
        try:
            cursor = self.collection.find({"style": style})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding rhythm patterns by style: {e}")
            return []

    async def find_by_tags(self, tags: List[str]) -> List[RhythmPattern]:
        """
        Find rhythm patterns by tags.
        
        Args:
            tags: List of tags to search for
            
        Returns:
            List of RhythmPattern instances
        """
        try:
            cursor = self.collection.find({"tags": {"$in": tags}})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding rhythm patterns by tags: {e}")
            return []
