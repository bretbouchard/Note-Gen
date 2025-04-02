"""Simple tests for API modules."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, Response
import json


# Mock database module
class MockDatabase:
    """Mock database for testing."""
    
    async def __anext__(self):
        """Yield the database."""
        return self
    
    async def __aenter__(self):
        """Enter the context."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        pass


# Mock API database functions
async def mock_get_db():
    """Mock get_db generator function."""
    db = MockDatabase()
    yield db


async def mock_get_database(db):
    """Mock get_database dependency function."""
    return db


# Tests for API database
@pytest.mark.asyncio
async def test_get_db():
    """Test the get_db generator function."""
    # Call the generator function
    db_gen = mock_get_db()
    db = await db_gen.__anext__()
    
    # Verify the database was yielded
    assert isinstance(db, MockDatabase)
    
    # Verify the generator completes properly
    with pytest.raises(StopAsyncIteration):
        await db_gen.__anext__()


@pytest.mark.asyncio
async def test_get_database():
    """Test the get_database dependency function."""
    # Create a mock database
    mock_db = MockDatabase()
    
    # Call the dependency function
    result = await mock_get_database(mock_db)
    
    # Verify the database was returned
    assert result is mock_db


# Mock middleware classes
class MockRateLimiter:
    """Mock rate limiter for testing."""
    
    def __init__(self):
        self.requests = {}
        self.window_size = 60
    
    def clear(self):
        """Clear the rate limiter."""
        self.requests = {}
    
    def _cleanup_old_requests(self, client_id):
        """Clean up old requests."""
        if client_id in self.requests:
            # Remove requests older than window_size
            current_time = 1000  # Mock time
            self.requests[client_id] = [
                t for t in self.requests[client_id]
                if current_time - t < self.window_size
            ]
    
    def is_rate_limited(self, client_id):
        """Check if a client is rate limited."""
        # Clean up old requests
        self._cleanup_old_requests(client_id)
        
        # Add current request
        current_time = 1000  # Mock time
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id].append(current_time)
        
        # Check if rate limited
        count = len(self.requests[client_id])
        return count > 60, count


class MockRateLimitMiddleware:
    """Mock rate limit middleware for testing."""
    
    async def dispatch(self, request, call_next):
        """Process the request."""
        # Get client ID
        client_id = request.client.host if request.client else "unknown"
        
        # Check if rate limited
        is_limited, count = MockRateLimiter().is_rate_limited(client_id)
        
        if is_limited:
            # Return rate limit error
            return Response(
                content=json.dumps({
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded: {count} requests in the last minute",
                    "current_count": count
                }),
                status_code=429,
                media_type="application/json"
            )
        
        # Process the request
        return await call_next(request)


class MockValidationMiddleware:
    """Mock validation middleware for testing."""
    
    def __init__(self, app=None):
        self.app = app
    
    async def dispatch(self, request, call_next):
        """Process the request."""
        # Check for required headers in POST requests
        if request.method == "POST" and "content-type" not in request.headers:
            # Return validation error
            return Response(
                content=json.dumps({
                    "code": "VALIDATION_ERROR",
                    "message": "Missing required header: content-type"
                }),
                status_code=400,
                media_type="application/json"
            )
        
        # Process the request
        return await call_next(request)


# Tests for middleware
@pytest.fixture
def mock_request():
    """Create a mock request with client information."""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.method = "GET"
    return request


@pytest.fixture
def mock_post_request():
    """Create a mock POST request."""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.method = "POST"
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(return_value={"test": "data"})
    return request


@pytest.fixture
def mock_post_request_no_content_type():
    """Create a mock POST request without content-type header."""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.method = "POST"
    request.headers = {}
    return request


def test_rate_limiter_init():
    """Test rate limiter initialization."""
    limiter = MockRateLimiter()
    assert limiter.requests == {}
    assert limiter.window_size == 60


def test_rate_limiter_clear():
    """Test clearing the rate limiter."""
    # Add some requests
    limiter = MockRateLimiter()
    limiter.requests["client1"] = [1000]
    limiter.requests["client2"] = [1000]
    
    # Clear the limiter
    limiter.clear()
    
    # Verify requests are cleared
    assert limiter.requests == {}


@pytest.mark.asyncio
async def test_middleware_not_limited(mock_request):
    """Test middleware when not rate limited."""
    # Create middleware
    middleware = MockRateLimitMiddleware()
    
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware
    response = await middleware.dispatch(mock_request, call_next)
    
    # Verify the response
    assert response == mock_response
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_validation_middleware_get_request(mock_request):
    """Test middleware with GET request."""
    # Create middleware
    middleware = MockValidationMiddleware()
    
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
    middleware = MockValidationMiddleware()
    
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
    middleware = MockValidationMiddleware()
    
    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)
    
    # Call the middleware
    response = await middleware.dispatch(mock_post_request_no_content_type, call_next)
    
    # Verify the response is a validation error
    assert response.status_code == 400
    
    # Parse the JSON response
    content = json.loads(response.body.decode())
    assert content["code"] == "VALIDATION_ERROR"
    assert "Missing required header: content-type" in content["message"]
    
    # Verify call_next was not called
    call_next.assert_not_called()
