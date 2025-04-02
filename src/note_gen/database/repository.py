from typing import TypeVar, Generic, Optional, Any, cast, Type, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class MongoDBRepository(Generic[T]):
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str, model_type: Optional[Type[T]] = None):
        self.collection = database[collection_name]
        # Store the actual type for runtime type checking
        # Try to get the type from __orig_class__ if available, otherwise use the provided model_type
        try:
            self._type = self.__orig_class__.__args__[0] if hasattr(self, '__orig_class__') else model_type
        except (AttributeError, IndexError):
            if model_type is None:
                raise ValueError("model_type must be provided if __orig_class__ is not available")
            self._type = model_type

    async def insert_one(self, model: T) -> str:
        # Use model_dump() instead of dict() for Pydantic v2
        result = await self.collection.insert_one(model.model_dump())
        return str(result.inserted_id)

    async def find_one(self, filter_dict: dict) -> Optional[T]:
        result = await self.collection.find_one(filter_dict)
        if result:
            # Use the stored concrete type instead of T
            # Cast to Type[T] to help mypy understand the type
            model_class = cast(Type[T], self._type)
            return model_class.model_validate(result)
        return None

    async def get_by_id(self, id: str) -> Optional[T]:
        """Get a document by its ID."""
        try:
            result = await self.collection.find_one({"_id": ObjectId(id)})
            if result:
                # Convert ObjectId to string for the response
                result["_id"] = str(result["_id"])
                # Add id field for compatibility
                result["id"] = result["_id"]
                # Cast to Type[T] to help mypy understand the type
                model_class = cast(Type[T], self._type)
                return model_class.model_validate(result)
            return None
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error in get_by_id: {e}")
            return None

    async def insert_many(self, models: List[T]) -> List[str]:
        """Insert multiple documents."""
        # Convert models to dictionaries
        documents = [model.model_dump() for model in models]
        result = await self.collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    async def find_many(self, filter_dict: dict) -> List[T]:
        """Find multiple documents matching the filter."""
        cursor = self.collection.find(filter_dict)
        results = []
        async for document in cursor:
            model_class = cast(Type[T], self._type)
            results.append(model_class.model_validate(document))
        return results

    async def update_one(self, filter_dict: dict, update_dict: dict):
        """Update a single document matching the filter."""
        return await self.collection.update_one(filter_dict, update_dict)

    async def update_many(self, filter_dict: dict, update_dict: dict):
        """Update multiple documents matching the filter."""
        return await self.collection.update_many(filter_dict, update_dict)

    async def delete_one(self, filter_dict: dict):
        """Delete a single document matching the filter."""
        return await self.collection.delete_one(filter_dict)

    async def delete_many(self, filter_dict: dict):
        """Delete multiple documents matching the filter."""
        return await self.collection.delete_many(filter_dict)

    async def count_documents(self, filter_dict: dict) -> int:
        """Count documents matching the filter."""
        return await self.collection.count_documents(filter_dict)
