"""Tests for database errors."""
import pytest
from note_gen.database.errors import (
    DatabaseError,
    ConnectionError,
    QueryError,
    DocumentNotFoundError,
    ValidationError
)


def test_database_error():
    """Test DatabaseError."""
    error = DatabaseError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_connection_error():
    """Test ConnectionError."""
    error = ConnectionError("Connection failed")
    assert str(error) == "Connection failed"
    assert isinstance(error, DatabaseError)


def test_query_error():
    """Test QueryError."""
    error = QueryError("Query failed")
    assert str(error) == "Query failed"
    assert isinstance(error, DatabaseError)


def test_document_not_found_error():
    """Test DocumentNotFoundError."""
    error = DocumentNotFoundError("123", "test_collection")
    assert str(error) == "Document '123' not found in collection 'test_collection'"
    assert isinstance(error, DatabaseError)
    assert error.document_id == "123"
    assert error.collection == "test_collection"


def test_validation_error_with_string():
    """Test ValidationError with string message."""
    error = ValidationError("Validation failed")
    assert str(error) == "Validation failed"
    assert isinstance(error, DatabaseError)
    assert error.errors == {"message": "Validation failed"}


def test_validation_error_with_dict():
    """Test ValidationError with dictionary of errors."""
    errors = {"field1": "Invalid value", "field2": "Required field"}
    error = ValidationError(errors)
    assert str(error) == str(errors)
    assert isinstance(error, DatabaseError)
    assert error.errors == errors
