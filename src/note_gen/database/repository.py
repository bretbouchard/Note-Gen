from typing import TypeVar, Generic, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class MongoDBRepository(Generic[T]):
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str, model_type: type[T] = None):
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
            return self._type.model_validate(result)
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
                return self._type.model_validate(result)
            return None
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error in get_by_id: {e}")
            return None
