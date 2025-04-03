"""Rhythm pattern repository implementation for the MCP architecture."""
from typing import List, Optional, Dict, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from note_gen.database.repositories.mongodb_repository import MongoDBRepository
from note_gen.models.rhythm import RhythmPattern, RhythmNote

class RhythmPatternRepository(MongoDBRepository[RhythmPattern]):
    """Repository for rhythm pattern operations."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """
        Initialize the rhythm pattern repository.

        Args:
            collection: MongoDB collection to use
        """
        super().__init__(collection, RhythmPattern)

    def _convert_to_model(self, data: Dict[str, Any]) -> RhythmPattern:
        """
        Convert dictionary data to RhythmPattern instance with proper handling of RhythmNote objects.

        Args:
            data: Dictionary data from MongoDB

        Returns:
            RhythmPattern instance
        """
        if data is None:
            raise ValueError("Data cannot be None")

        # Convert MongoDB _id to string id
        if "_id" in data:
            data["id"] = str(data["_id"])
            del data["_id"]

        # Handle pattern field - convert dictionaries to RhythmNote objects
        if "pattern" in data and isinstance(data["pattern"], list):
            pattern_notes = []
            for note_data in data["pattern"]:
                if isinstance(note_data, dict):
                    # Create RhythmNote object from dictionary
                    try:
                        note = RhythmNote(**note_data)
                        pattern_notes.append(note)
                    except Exception as e:
                        print(f"Error converting rhythm note: {e}")
                        # Skip this note
                else:
                    # If it's already a RhythmNote object or string, keep it as is
                    pattern_notes.append(note_data)
            data["pattern"] = pattern_notes

        # Convert to model
        try:
            return RhythmPattern.model_validate(data)
        except Exception as e:
            print(f"Error creating RhythmPattern: {e}")
            raise

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
            result = []
            for doc in documents:
                if doc:
                    try:
                        pattern = self._convert_to_model(doc)
                        result.append(pattern)
                    except Exception as e:
                        print(f"Error converting document: {e}")
            return result
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
            result = []
            for doc in documents:
                if doc:
                    try:
                        pattern = self._convert_to_model(doc)
                        result.append(pattern)
                    except Exception as e:
                        print(f"Error converting document: {e}")
            return result
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
            result = []
            for doc in documents:
                if doc:
                    try:
                        pattern = self._convert_to_model(doc)
                        result.append(pattern)
                    except Exception as e:
                        print(f"Error converting document: {e}")
            return result
        except Exception as e:
            # Log the error
            print(f"Error finding rhythm patterns by tags: {e}")
            return []
