"""Tests for database exceptions."""
import pytest
from note_gen.database.exceptions import (
    DatabaseError,
    ConnectionError,
    DuplicateKeyError,
    DuplicateDocumentError,
    DocumentNotFoundError,
    ValidationError,
    TransactionError
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


def test_duplicate_key_error():
    """Test DuplicateKeyError."""
    error = DuplicateKeyError("Duplicate key")
    assert str(error) == "Duplicate key"
    assert isinstance(error, DatabaseError)


def test_duplicate_document_error():
    """Test DuplicateDocumentError."""
    error = DuplicateDocumentError("Duplicate document")
    assert str(error) == "Duplicate document"
    assert isinstance(error, DatabaseError)


def test_document_not_found_error():
    """Test DocumentNotFoundError."""
    error = DocumentNotFoundError("Document not found")
    assert str(error) == "Document not found"
    assert isinstance(error, DatabaseError)


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Validation failed")
    assert str(error) == "Validation failed"
    assert isinstance(error, DatabaseError)


def test_transaction_error():
    """Test TransactionError."""
    error = TransactionError("Transaction failed")
    assert str(error) == "Transaction failed"
    assert isinstance(error, DatabaseError)
