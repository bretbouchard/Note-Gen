"""Tests for validation middleware."""
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import Request
from starlette.responses import Response
from note_gen.api.middleware.validation import ValidationMiddleware, validate_request_middleware
from note_gen.api.errors import ErrorCodes
import json


@pytest.fixture
def mock_app():
    """Create a mock ASGI app."""
    return MagicMock()


@pytest.fixture
def mock_request():
    """Create a mock request."""
    request = MagicMock(spec=Request)
    request.method = "GET"
    request.headers = {"content-type": "application/json"}
    return request


@pytest.fixture
def mock_post_request():
    """Create a mock POST request with content-type header."""
    request = MagicMock(spec=Request)
    request.method = "POST"
    request.headers = {"content-type": "application/json"}
    return request


@pytest.fixture
def mock_post_request_no_content_type():
    """Create a mock POST request without content-type header."""
    request = MagicMock(spec=Request)
    request.method = "POST"
    request.headers = {}
    return request


def test_validation_middleware_init(mock_app):
    """Test middleware initialization."""
    middleware = ValidationMiddleware(mock_app)
    assert middleware.app == mock_app


@pytest.mark.asyncio
async def test_validation_middleware_get_request(mock_request):
    """Test middleware with GET request."""
    # Create middleware
    middleware = ValidationMiddleware(MagicMock())
    
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware
    response = await middleware.dispatch(mock_request, call_next)
    
    # Verify the response
    assert response == mock_response
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_validation_middleware_post_with_content_type(mock_post_request):
    """Test middleware with POST request that has content-type header."""
    # Create middleware
    middleware = ValidationMiddleware(MagicMock())
    
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware
    response = await middleware.dispatch(mock_post_request, call_next)
    
    # Verify the response
    assert response == mock_response
    call_next.assert_called_once_with(mock_post_request)


@pytest.mark.asyncio
async def test_validation_middleware_post_without_content_type(mock_post_request_no_content_type):
    """Test middleware with POST request that has no content-type header."""
    # Create middleware
    middleware = ValidationMiddleware(MagicMock())
    
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware
    response = await middleware.dispatch(mock_post_request_no_content_type, call_next)
    
    # Verify the response is a validation error
    assert response.status_code == 400
    
    # Parse the JSON response
    content = json.loads(response.body.decode())
    assert content["code"] == ErrorCodes.VALIDATION_ERROR.value
    assert "Missing required header: content-type" in content["message"]
    
    # Verify call_next was not called
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_validate_request_middleware_get_request(mock_request):
    """Test standalone middleware function with GET request."""
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware function
    response = await validate_request_middleware(mock_request, call_next)
    
    # Verify the response
    assert response == mock_response
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_validate_request_middleware_post_with_content_type(mock_post_request):
    """Test standalone middleware function with POST request that has content-type header."""
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware function
    response = await validate_request_middleware(mock_post_request, call_next)
    
    # Verify the response
    assert response == mock_response
    call_next.assert_called_once_with(mock_post_request)


@pytest.mark.asyncio
async def test_validate_request_middleware_post_without_content_type(mock_post_request_no_content_type):
    """Test standalone middleware function with POST request that has no content-type header."""
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware function
    response = await validate_request_middleware(mock_post_request_no_content_type, call_next)
    
    # Verify the response is a validation error
    assert response.status_code == 400
    
    # Parse the JSON response
    content = json.loads(response.body.decode())
    assert content["code"] == ErrorCodes.VALIDATION_ERROR.value
    assert "Missing required header: content-type" in content["message"]
    
    # Verify call_next was not called
    call_next.assert_not_called()
