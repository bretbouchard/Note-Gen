"""Database exceptions."""

class DatabaseError(Exception):
    """Base exception for database errors."""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

class DuplicateKeyError(DatabaseError):
    """Raised when attempting to insert a document with a duplicate key."""
    pass

class DuplicateDocumentError(DatabaseError):
    """Raised when attempting to insert a duplicate document."""
    pass

class DocumentNotFoundError(DatabaseError):
    """Raised when a document is not found in the database."""
    pass

class ValidationError(DatabaseError):
    """Raised when document validation fails."""
    pass

class TransactionError(DatabaseError):
    """Raised when a database transaction fails."""
    pass
