from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Generic, TypeVar, Optional, List, Dict, Any
from .interfaces import Repository
from .retry import with_retry
from .validation import DocumentValidator
from .errors import DatabaseError

T = TypeVar('T')

class MongoRepository(Repository[T], Generic[T]):
    """Enhanced base MongoDB repository implementation."""
    
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self.collection = database[collection_name]
        self.validator = DocumentValidator()
    
    @with_retry()
    async def find_one(self, id: str) -> Optional[T]:
        doc = await self.collection.find_one({"_id": id})
        return self._convert_to_model(doc) if doc else None
    
    @with_retry()
    async def find_many(self, filter_dict: Dict[str, Any]) -> List[T]:
        cursor = self.collection.find(filter_dict)
        documents = await cursor.to_list(length=None)
        return [self._convert_to_model(doc) for doc in documents]
    
    @with_retry()
    async def create(self, document: T) -> T:
        doc_dict = self._convert_to_dict(document)
        # Validate before insertion
        self.validator.validate_document(type(document), doc_dict)
        result = await self.collection.insert_one(doc_dict)
        return document
    
    @with_retry()
    async def update(self, id: str, document: T) -> Optional[T]:
        doc_dict = self._convert_to_dict(document)
        # Validate before update
        self.validator.validate_document(type(document), doc_dict)
        result = await self.collection.replace_one({"_id": id}, doc_dict)
        return document if result.modified_count > 0 else None
    
    @with_retry()
    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
    
    async def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        # Validate update operations
        validated_update = self.validator.validate_update(self._get_model_class(), update_dict)
        result = await self.collection.update_many(filter_dict, validated_update)
        return result.modified_count
    
    def _get_model_class(self) -> type:
        """Get the model class for this repository."""
        raise NotImplementedError
    
    def _convert_to_model(self, doc: Dict) -> T:
        """Override in concrete repositories to convert dict to model."""
        raise NotImplementedError
    
    def _convert_to_dict(self, model: T) -> Dict:
        """Override in concrete repositories to convert model to dict."""
        raise NotImplementedError