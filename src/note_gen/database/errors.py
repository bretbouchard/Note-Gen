from typing import Dict, Any, Union
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import (
    ConnectionFailure, 
    OperationFailure, 
    ServerSelectionTimeoutError,
    WriteError
)

"""Database-related exceptions."""

class DatabaseError(Exception):
    """Base class for database errors."""
    pass

class ConnectionError(DatabaseError):
    """Raised when a database connection fails."""
    pass

class QueryError(DatabaseError):
    """Raised when a database query fails."""
    pass

class DocumentNotFoundError(DatabaseError):
    """Raised when a document is not found in the database."""
    def __init__(self, document_id: str, collection: str):
        self.document_id = document_id
        self.collection = collection
        message = f"Document '{document_id}' not found in collection '{collection}'"
        super().__init__(message)

class ValidationError(DatabaseError):
    """Raised when document validation fails."""
    def __init__(self, errors: Union[str, Dict[str, Any]]):
        self.errors = errors if isinstance(errors, dict) else {"message": str(errors)}
        message = str(errors) if isinstance(errors, str) else str(self.errors)
        super().__init__(message)
