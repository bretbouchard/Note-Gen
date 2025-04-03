"""Tests for API error handlers."""
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from note_gen.api.middleware.error_handlers import setup_error_handlers
from note_gen.database.errors import ConnectionError, DocumentNotFoundError
from note_gen.api.errors import ErrorCodes


@pytest.fixture
def app():
    """Create a FastAPI app for testing."""
    app = FastAPI()
    # Setup error handlers directly
    setup_error_handlers(app)
    return app


@pytest.fixture
def request_mock():
    """Create a mock request."""
    return MagicMock(spec=Request)


def test_setup_error_handlers(app):
    """Test that error handlers are properly registered."""
    # Check that exception handlers were registered
    assert app.exception_handlers.get(ConnectionError) is not None
    assert app.exception_handlers.get(DocumentNotFoundError) is not None
    assert app.exception_handlers.get(RequestValidationError) is not None


@pytest.mark.asyncio
async def test_database_error_handler(app, request_mock):
    """Test the database error handler."""
    # Get the handler function
    handler = app.exception_handlers.get(ConnectionError)
    
    # Create an exception
    exc = ConnectionError("Database connection failed")
    
    # Call the handler
    response = await handler(request_mock, exc)
    
    # Verify the response
    assert response.status_code == 500
    assert response.body is not None
    
    # Parse the JSON response
    content = response.body.decode()
    assert f'"{ErrorCodes.DATABASE_ERROR.value}"' in content
    assert "Database error: Database connection failed" in content


@pytest.mark.asyncio
async def test_document_not_found_handler(app, request_mock):
    """Test the document not found handler."""
    # Get the handler function
    handler = app.exception_handlers.get(DocumentNotFoundError)
    
    # Create an exception
    exc = DocumentNotFoundError(document_id="123", collection="test_collection")
    
    # Call the handler
    response = await handler(request_mock, exc)
    
    # Verify the response
    assert response.status_code == 404
    assert response.body is not None
    
    # Parse the JSON response
    content = response.body.decode()
    assert f'"{ErrorCodes.NOT_FOUND.value}"' in content
    assert "Document '123' not found in collection 'test_collection'" in content


@pytest.mark.asyncio
async def test_validation_error_handler(app, request_mock):
    """Test the validation error handler."""
    # Get the handler function
    handler = app.exception_handlers.get(RequestValidationError)
    
    # Create an exception with errors
    exc = RequestValidationError(errors=[{"loc": ["body", "name"], "msg": "field required"}])
    
    # Call the handler
    response = await handler(request_mock, exc)
    
    # Verify the response
    assert response.status_code == 422
    assert response.body is not None
    
    # Parse the JSON response
    content = response.body.decode()
    assert f'"{ErrorCodes.VALIDATION_ERROR.value}"' in content
    assert "Validation error" in content
    assert "field required" in content
