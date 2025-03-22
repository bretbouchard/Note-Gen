from typing import Type, TypeVar
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import (
    ConnectionFailure, 
    OperationFailure, 
    ServerSelectionTimeoutError,
    WriteError
)

"""Database-related exceptions."""

class DatabaseError(Exception):
    """Base class for database-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

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
    def __init__(self, errors: dict):
        self.errors = errors
        message = "Document validation failed"
        super().__init__(message)
