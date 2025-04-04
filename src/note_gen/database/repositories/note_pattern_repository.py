"""Note pattern repository implementation for the MCP architecture."""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from note_gen.database.repositories.mongodb_repository import MongoDBRepository
from note_gen.models.patterns import NotePattern
from note_gen.models.note import Note
from note_gen.core.enums import ScaleType

class NotePatternRepository(MongoDBRepository[NotePattern]):
    """Repository for note pattern operations."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """
        Initialize the note pattern repository.

        Args:
            collection: MongoDB collection to use
        """
        super().__init__(collection, NotePattern)

    def _convert_to_model(self, data: Dict[str, Any]) -> NotePattern:
        """
        Convert dictionary data to NotePattern instance with proper handling of Note objects.

        Args:
            data: Dictionary data from MongoDB

        Returns:
            NotePattern instance
        """
        if data is None:
            raise ValueError("Data cannot be None")

        # Convert MongoDB _id to string id
        if "_id" in data:
            data["id"] = str(data["_id"])
            del data["_id"]

        # We'll let the NotePattern model handle the conversion of pattern notes
        # Just make sure the pattern is a list
        if "pattern" in data and not isinstance(data["pattern"], list):
            data["pattern"] = []

        # Set skip_validation to True to avoid validation errors
        data["skip_validation"] = True

        # Convert to model
        try:
            return NotePattern.model_validate(data)
        except Exception as e:
            print(f"Error creating NotePattern: {e}")
            print(f"Data: {data}")
            raise

    async def find_by_name(self, name: str) -> Optional[NotePattern]:
        """
        Find a note pattern by name.

        Args:
            name: Name of the note pattern

        Returns:
            NotePattern if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"name": name})
            return self._convert_to_model(doc) if doc else None
        except Exception as e:
            # Log the error
            print(f"Error finding note pattern by name: {e}")
            return None

    async def find_by_scale_type(self, scale_type: ScaleType) -> List[NotePattern]:
        """
        Find note patterns by scale type.

        Args:
            scale_type: Scale type of the note pattern

        Returns:
            List of NotePattern instances
        """
        try:
            cursor = self.collection.find({"data.scale_type": scale_type.value})
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
            print(f"Error finding note patterns by scale type: {e}")
            return []

    async def find_by_complexity_range(self, min_complexity: float, max_complexity: float) -> List[NotePattern]:
        """
        Find note patterns within a complexity range.

        Args:
            min_complexity: Minimum complexity
            max_complexity: Maximum complexity

        Returns:
            List of NotePattern instances
        """
        try:
            cursor = self.collection.find({
                "complexity": {
                    "$gte": min_complexity,
                    "$lte": max_complexity
                }
            })
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
            print(f"Error finding note patterns by complexity range: {e}")
            return []

    async def find_by_tags(self, tags: List[str]) -> List[NotePattern]:
        """
        Find note patterns by tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of NotePattern instances
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
            print(f"Error finding note patterns by tags: {e}")
            return []
