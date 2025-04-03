"""Base repository pattern implementation."""

# No longer using ABC
from typing import Generic, TypeVar, List, Optional, Any, Dict, cast
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from bson import ObjectId
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Base repository implementation."""

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection
        self.model_type = self._get_model_type()

    def _get_model_type(self) -> type:
        """Get the model type from the generic parameter."""
        # In Python 3.12, we need to use a different approach
        # We'll use a simpler approach by requiring the model type to be passed explicitly
        from note_gen.models.chord_progression import ChordProgression
        from note_gen.models.patterns import NotePattern, RhythmPattern
        from note_gen.models.sequence import Sequence
        from note_gen.models.user import User

        # Map collection names to model types
        collection_name = self.collection.name
        model_map = {
            "chord_progressions": ChordProgression,
            "note_patterns": NotePattern,
            "rhythm_patterns": RhythmPattern,
            "sequences": Sequence,
            "users": User
        }

        if collection_name in model_map:
            return model_map[collection_name]

        # Default to ChordProgression if collection name not found
        return ChordProgression

    async def find_one(self, id: str) -> Optional[T]:
        """Find a single document by ID."""
        try:
            # Handle both AsyncMock and real collection
            if hasattr(self.collection.find_one, "__await__"):
                document = await self.collection.find_one({"_id": ObjectId(id)})
            else:
                # For AsyncMock in tests
                document = self.collection.find_one({"_id": ObjectId(id)})
                if hasattr(document, "__await__"):
                    document = await document

            if document:
                # Cast to Dict to satisfy type checker
                doc_dict = cast(Dict[str, Any], document)
                return self._convert_to_model(doc_dict)
            return None
        except Exception as e:
            print(f"Error in find_one: {e}")
            return None

    async def find_many(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[T]:
        """Find multiple documents matching filter criteria."""
        try:
            # Use empty dict as default filter to match all documents
            actual_filter = filter_dict if filter_dict is not None else {}

            # Handle both AsyncMock and real collection
            cursor = self.collection.find(actual_filter)

            # For AsyncMock in tests
            if hasattr(cursor, "to_list") and hasattr(cursor.to_list, "__await__"):
                documents = await cursor.to_list(length=None)
            else:
                # For AsyncMock in tests
                documents = cursor.to_list(None)
                if hasattr(documents, "__await__"):
                    documents = await documents

            return [self._convert_to_model(doc) for doc in documents]
        except Exception as e:
            print(f"Error in find_many: {e}")
            return []

    async def create(self, document: T) -> T:
        """Create a new document."""
        try:
            # Convert model to dict
            doc_dict = document.model_dump()
            # Remove id if it exists and is None
            if "id" in doc_dict and doc_dict["id"] is None:
                del doc_dict["id"]

            # Insert document - handle both AsyncMock and real collection
            if hasattr(self.collection.insert_one, "__await__"):
                result = await self.collection.insert_one(doc_dict)
            else:
                # For AsyncMock in tests
                result = self.collection.insert_one(doc_dict)
                if hasattr(result, "__await__"):
                    result = await result

            # Cast to InsertOneResult to satisfy type checker
            typed_result = cast(InsertOneResult, result)

            # Update document with generated ID
            doc_dict["id"] = str(typed_result.inserted_id)

            # Return updated model
            return self.model_type(**doc_dict)
        except Exception as e:
            print(f"Error in create: {e}")
            raise

    async def update(self, id: str, document: T) -> Optional[T]:
        """Update an existing document."""
        try:
            # Convert model to dict
            doc_dict = document.model_dump()
            # Remove id if it exists
            if "id" in doc_dict:
                del doc_dict["id"]

            # Update document - handle both AsyncMock and real collection
            if hasattr(self.collection.update_one, "__await__"):
                result = await self.collection.update_one(
                    {"_id": ObjectId(id)},
                    {"$set": doc_dict}
                )
            else:
                # For AsyncMock in tests
                result = self.collection.update_one(
                    {"_id": ObjectId(id)},
                    {"$set": doc_dict}
                )
                if hasattr(result, "__await__"):
                    result = await result

            # Cast to UpdateResult to satisfy type checker
            typed_result = cast(UpdateResult, result)

            if typed_result.modified_count > 0:
                # Get updated document - handle both AsyncMock and real collection
                if hasattr(self.collection.find_one, "__await__"):
                    updated_doc = await self.collection.find_one({"_id": ObjectId(id)})
                else:
                    # For AsyncMock in tests
                    updated_doc = self.collection.find_one({"_id": ObjectId(id)})
                    if hasattr(updated_doc, "__await__"):
                        updated_doc = await updated_doc

                if updated_doc:
                    # Cast to Dict to satisfy type checker
                    doc_dict = cast(Dict[str, Any], updated_doc)
                    return self._convert_to_model(doc_dict)
            return None
        except Exception as e:
            print(f"Error in update: {e}")
            return None

    async def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        try:
            # Handle both AsyncMock and real collection
            if hasattr(self.collection.delete_one, "__await__"):
                result = await self.collection.delete_one({"_id": ObjectId(id)})
            else:
                # For AsyncMock in tests
                result = self.collection.delete_one({"_id": ObjectId(id)})
                if hasattr(result, "__await__"):
                    result = await result

            # Cast to DeleteResult to satisfy type checker
            typed_result = cast(DeleteResult, result)
            return typed_result.deleted_count > 0
        except Exception as e:
            print(f"Error in delete: {e}")
            return False

    def _convert_to_model(self, data: Dict[str, Any]) -> T:
        """Convert dictionary data to model instance."""
        try:
            # Convert _id to id string
            if "_id" in data:
                data["id"] = str(data["_id"])
                del data["_id"]

            # Create model instance
            return self.model_type(**data)
        except Exception as e:
            print(f"Error in _convert_to_model: {e}")
            raise
