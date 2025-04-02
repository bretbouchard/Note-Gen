"""Chord progression repository implementation for the MCP architecture."""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from note_gen.database.repositories.mongodb_repository import MongoDBRepository
from note_gen.models.chord_progression import ChordProgression
from note_gen.core.enums import ScaleType

class ChordProgressionRepository(MongoDBRepository[ChordProgression]):
    """Repository for chord progression operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """
        Initialize the chord progression repository.
        
        Args:
            collection: MongoDB collection to use
        """
        super().__init__(collection, ChordProgression)

    async def find_by_name(self, name: str) -> Optional[ChordProgression]:
        """
        Find a chord progression by name.
        
        Args:
            name: Name of the chord progression
            
        Returns:
            ChordProgression if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"name": name})
            return self._convert_to_model(doc) if doc else None
        except Exception as e:
            # Log the error
            print(f"Error finding chord progression by name: {e}")
            return None

    async def find_by_key(self, key: str) -> List[ChordProgression]:
        """
        Find chord progressions by key.
        
        Args:
            key: Key of the chord progression
            
        Returns:
            List of ChordProgression instances
        """
        try:
            cursor = self.collection.find({"key": key})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding chord progressions by key: {e}")
            return []

    async def find_by_scale_type(self, scale_type: ScaleType) -> List[ChordProgression]:
        """
        Find chord progressions by scale type.
        
        Args:
            scale_type: Scale type of the chord progression
            
        Returns:
            List of ChordProgression instances
        """
        try:
            cursor = self.collection.find({"scale_type": scale_type.value})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding chord progressions by scale type: {e}")
            return []

    async def find_by_tags(self, tags: List[str]) -> List[ChordProgression]:
        """
        Find chord progressions by tags.
        
        Args:
            tags: List of tags to search for
            
        Returns:
            List of ChordProgression instances
        """
        try:
            cursor = self.collection.find({"tags": {"$in": tags}})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding chord progressions by tags: {e}")
            return []

    async def find_by_complexity_range(self, min_complexity: float, max_complexity: float) -> List[ChordProgression]:
        """
        Find chord progressions within a complexity range.
        
        Args:
            min_complexity: Minimum complexity
            max_complexity: Maximum complexity
            
        Returns:
            List of ChordProgression instances
        """
        try:
            cursor = self.collection.find({
                "complexity": {
                    "$gte": min_complexity,
                    "$lte": max_complexity
                }
            })
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding chord progressions by complexity range: {e}")
            return []
