"""Custom exceptions for the application."""
from fastapi import HTTPException, status

class DocumentNotFoundError(HTTPException):
    """Raised when a document is not found in the database."""
    def __init__(self, detail: str = "Document not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class DatabaseError(HTTPException):
    """Raised when a database operation fails."""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class ValidationError(HTTPException):
    """Raised when validation fails."""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)