"""Tests for rate limiting middleware."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import Request
from starlette.responses import Response
from src.note_gen.api.middleware.rate_limit import RateLimiter, RateLimitMiddleware, rate_limiter
from src.note_gen.api.errors import ErrorCodes
import time
import json


@pytest.fixture
def limiter():
    """Create a fresh rate limiter for testing."""
    limiter = RateLimiter()
    limiter.clear()
    return limiter


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
    request.json = AsyncMock(return_value={"test": "data"})
    return request


@pytest.fixture
def mock_invalid_json_request():
    """Create a mock POST request with invalid JSON."""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.method = "POST"
    request.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
    return request


def test_rate_limiter_init(limiter):
    """Test rate limiter initialization."""
    assert limiter.requests == {}
    assert limiter.window_size == 60


def test_rate_limiter_cleanup(limiter):
    """Test cleaning up old requests."""
    # Add some requests
    client_id = "test_client"
    current_time = time.time()

    # Add an old request and a new request
    limiter.requests[client_id] = [
        current_time - 120,  # Old request (2 minutes ago)
        current_time - 10    # Recent request (10 seconds ago)
    ]

    # Clean up old requests
    limiter._cleanup_old_requests(client_id)

    # Verify only the recent request remains
    assert len(limiter.requests[client_id]) == 1
    assert current_time - limiter.requests[client_id][0] < 60


def test_rate_limiter_not_limited(limiter):
    """Test rate limiter when not exceeding limits."""
    client_id = "test_client"

    # Check if rate limited (should not be)
    is_limited, count = limiter.is_rate_limited(client_id)

    # Verify not rate limited
    assert is_limited is False
    assert count == 1
    assert client_id in limiter.requests
    assert len(limiter.requests[client_id]) == 1


def test_rate_limiter_is_limited(limiter):
    """Test rate limiter when exceeding limits."""
    client_id = "test_client"
    current_time = time.time()

    # Add many requests to exceed the limit
    limiter.requests[client_id] = [current_time - i for i in range(70)]

    # Check if rate limited (should be)
    with patch('src.note_gen.api.middleware.rate_limit.RATE_LIMIT', {"requests_per_minute": 60}):
        is_limited, count = limiter.is_rate_limited(client_id)

    # Verify rate limited
    assert is_limited is True
    assert count > 60


def test_rate_limiter_clear(limiter):
    """Test clearing the rate limiter."""
    # Add some requests
    limiter.requests["client1"] = [time.time()]
    limiter.requests["client2"] = [time.time()]

    # Clear the limiter
    limiter.clear()

    # Verify requests are cleared
    assert limiter.requests == {}


@pytest.mark.asyncio
async def test_middleware_not_limited(mock_request):
    """Test middleware when not rate limited."""
    # Create middleware
    middleware = RateLimitMiddleware(app=MagicMock())

    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)

    # Clear the rate limiter
    rate_limiter.clear()

    # Call the middleware
    response = await middleware.dispatch(mock_request, call_next)

    # Verify the response
    assert response == mock_response
    call_next.assert_called_once_with(mock_request)


@pytest.mark.asyncio
async def test_middleware_rate_limited(mock_request):
    """Test middleware when rate limited."""
    # Create middleware
    middleware = RateLimitMiddleware(app=MagicMock())

    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)

    # Clear the rate limiter
    rate_limiter.clear()

    # Add many requests to exceed the limit
    client_id = mock_request.client.host
    current_time = time.time()
    rate_limiter.requests[client_id] = [current_time - i for i in range(70)]

    # Call the middleware with rate limit patch
    with patch('src.note_gen.api.middleware.rate_limit.RATE_LIMIT',
               {"requests_per_minute": 60}):
        response = await middleware.dispatch(mock_request, call_next)

    # Verify the response is a rate limit error
    assert response.status_code == 429

    # Parse the JSON response
    content = json.loads(response.body.decode())
    assert content["code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value
    assert "Rate limit exceeded" in content["message"]
    assert content["current_count"] > 60

    # Verify call_next was not called
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_middleware_post_request(mock_post_request):
    """Test middleware with a valid POST request."""
    # Create middleware
    middleware = RateLimitMiddleware(app=MagicMock())

    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)

    # Clear the rate limiter
    rate_limiter.clear()

    # Call the middleware
    response = await middleware.dispatch(mock_post_request, call_next)

    # Verify the response
    assert response == mock_response
    call_next.assert_called_once_with(mock_post_request)
    mock_post_request.json.assert_called_once()


@pytest.mark.asyncio
async def test_middleware_invalid_json(mock_invalid_json_request):
    """Test middleware with invalid JSON in POST request."""
    # Create middleware
    middleware = RateLimitMiddleware(app=MagicMock())

    # Mock the call_next function
    mock_response = Response(content="OK")
    call_next = AsyncMock(return_value=mock_response)

    # Clear the rate limiter
    rate_limiter.clear()

    # Call the middleware
    response = await middleware.dispatch(mock_invalid_json_request, call_next)

    # Verify the response is a validation error
    assert response.status_code == 422

    # Parse the JSON response
    content = json.loads(response.body.decode())
    assert content["code"] == ErrorCodes.VALIDATION_ERROR.value
    assert "Invalid JSON data" in content["message"]

    # Verify call_next was not called
    call_next.assert_not_called()
    mock_invalid_json_request.json.assert_called_once()
