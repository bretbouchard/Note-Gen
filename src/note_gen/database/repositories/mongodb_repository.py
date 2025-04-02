"""MongoDB repository implementation for the MCP architecture."""
from typing import Generic, TypeVar, List, Optional, Any, Dict, Type, cast
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from note_gen.database.repositories.base import BaseRepository

T = TypeVar('T', bound=BaseModel)

class MongoDBRepository(BaseRepository[T]):
    """MongoDB implementation of the BaseRepository."""
    
    def __init__(self, collection: AsyncIOMotorCollection, model_class: Type[T]) -> None:
        """
        Initialize the MongoDB repository.
        
        Args:
            collection: MongoDB collection to use
            model_class: Model class to use for conversion
        """
        super().__init__(collection)
        self.model_class = model_class

    async def find_one(self, id: str) -> Optional[T]:
        """
        Find a single document by ID.
        
        Args:
            id: Document ID
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"_id": ObjectId(id)})
            return self._convert_to_model(doc) if doc else None
        except Exception as e:
            # Log the error
            print(f"Error finding document by ID: {e}")
            return None

    async def find_many(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Find multiple documents matching filter criteria.
        
        Args:
            filter_dict: Filter criteria
            
        Returns:
            List of model instances
        """
        try:
            # Use empty dict as default filter to match all documents
            actual_filter = filter_dict if filter_dict is not None else {}
            cursor = self.collection.find(actual_filter)
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding documents: {e}")
            return []

    async def create(self, document: T) -> T:
        """
        Create a new document.
        
        Args:
            document: Model instance to create
            
        Returns:
            Created model instance
        """
        try:
            # Convert model to dict for MongoDB
            doc_dict = document.model_dump(exclude_unset=True)
            
            # Remove ID if it's None
            if "_id" in doc_dict and doc_dict["_id"] is None:
                del doc_dict["_id"]
                
            # Insert document
            result = await self.collection.insert_one(doc_dict)
            
            # Set ID on the model
            document_dict = document.model_dump()
            document_dict["id"] = str(result.inserted_id)
            
            # Return updated model
            return self.model_class.model_validate(document_dict)
        except Exception as e:
            # Log the error
            print(f"Error creating document: {e}")
            raise

    async def update(self, id: str, document: T) -> Optional[T]:
        """
        Update an existing document.
        
        Args:
            id: Document ID
            document: Model instance with updated data
            
        Returns:
            Updated model instance if found, None otherwise
        """
        try:
            # Convert model to dict for MongoDB
            doc_dict = document.model_dump(exclude_unset=True)
            
            # Remove ID from update data
            if "_id" in doc_dict:
                del doc_dict["_id"]
            if "id" in doc_dict:
                del doc_dict["id"]
                
            # Update document
            result = await self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": doc_dict}
            )
            
            # Return updated document if found
            if result.matched_count > 0:
                updated_doc = await self.collection.find_one({"_id": ObjectId(id)})
                return self._convert_to_model(updated_doc) if updated_doc else None
            return None
        except Exception as e:
            # Log the error
            print(f"Error updating document: {e}")
            return None

    async def delete(self, id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            id: Document ID
            
        Returns:
            True if document was deleted, False otherwise
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            # Log the error
            print(f"Error deleting document: {e}")
            return False

    def _convert_to_model(self, data: Dict[str, Any]) -> T:
        """
        Convert dictionary data to model instance.
        
        Args:
            data: Dictionary data from MongoDB
            
        Returns:
            Model instance
        """
        if data is None:
            raise ValueError("Data cannot be None")
            
        # Convert MongoDB _id to string id
        if "_id" in data:
            data["id"] = str(data["_id"])
            del data["_id"]
            
        # Convert to model
        return self.model_class.model_validate(data)
