"""Sequence repository implementation for the MCP architecture."""
from typing import List, Optional, Dict, Any, Union, Type, TypeVar
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from note_gen.database.repositories.mongodb_repository import MongoDBRepository
from note_gen.models.sequence import Sequence
from note_gen.models.note_sequence import NoteSequence

T = TypeVar('T', bound=Sequence)

class SequenceRepository(MongoDBRepository[Sequence]):
    """Repository for sequence operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection, model_class: Type[Sequence] = Sequence) -> None:
        """
        Initialize the sequence repository.
        
        Args:
            collection: MongoDB collection to use
            model_class: Model class to use for conversion (default: Sequence)
        """
        super().__init__(collection, model_class)

    async def find_by_name(self, name: str) -> Optional[Sequence]:
        """
        Find a sequence by name.
        
        Args:
            name: Name of the sequence
            
        Returns:
            Sequence if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"name": name})
            return self._convert_to_model(doc) if doc else None
        except Exception as e:
            # Log the error
            print(f"Error finding sequence by name: {e}")
            return None

    async def find_by_pattern_name(self, pattern_name: str) -> List[NoteSequence]:
        """
        Find sequences by pattern name.
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            List of NoteSequence instances
        """
        try:
            cursor = self.collection.find({
                "$or": [
                    {"note_pattern_name": pattern_name},
                    {"rhythm_pattern_name": pattern_name}
                ]
            })
            documents = await cursor.to_list(length=None)
            return [NoteSequence.model_validate(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding sequences by pattern name: {e}")
            return []

    async def find_by_progression_name(self, progression_name: str) -> List[NoteSequence]:
        """
        Find sequences by progression name.
        
        Args:
            progression_name: Name of the chord progression
            
        Returns:
            List of NoteSequence instances
        """
        try:
            cursor = self.collection.find({"progression_name": progression_name})
            documents = await cursor.to_list(length=None)
            return [NoteSequence.model_validate(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding sequences by progression name: {e}")
            return []

    async def find_by_tags(self, tags: List[str]) -> List[Sequence]:
        """
        Find sequences by tags.
        
        Args:
            tags: List of tags to search for
            
        Returns:
            List of Sequence instances
        """
        try:
            cursor = self.collection.find({"metadata.tags": {"$in": tags}})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding sequences by tags: {e}")
            return []

    def _convert_to_model(self, data: Dict[str, Any]) -> Sequence:
        """
        Convert dictionary data to model instance.
        
        Args:
            data: Dictionary data from MongoDB
            
        Returns:
            Sequence instance
        """
        if data is None:
            raise ValueError("Data cannot be None")
            
        # Convert MongoDB _id to string id
        if "_id" in data:
            data["id"] = str(data["_id"])
            del data["_id"]
            
        # Check if this is a NoteSequence
        if "notes" in data:
            return NoteSequence.model_validate(data)
            
        # Otherwise, return a base Sequence
        return Sequence.model_validate(data)
