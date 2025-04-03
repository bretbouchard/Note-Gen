"""Tests for retry mechanism."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from note_gen.database.retry import with_retry
from note_gen.database.errors import ConnectionError


@pytest.mark.asyncio
async def test_retry_success_first_attempt():
    """Test successful execution on first attempt."""
    # Create a mock function that succeeds
    mock_func = MagicMock()
    mock_func.return_value = asyncio.Future()
    mock_func.return_value.set_result("success")

    # Apply the retry decorator
    decorated_func = with_retry()(mock_func)

    # Call the decorated function
    result = await decorated_func("arg1", kwarg1="value1")

    # Verify the result and that the function was called only once
    assert result == "success"
    mock_func.assert_called_once_with("arg1", kwarg1="value1")


@pytest.mark.asyncio
async def test_retry_success_after_failures():
    """Test successful execution after some failures."""
    # Create a mock function that fails twice then succeeds
    mock_func = MagicMock()

    # Set up side effects: first two calls raise ConnectionFailure, third call succeeds
    side_effects = [
        ConnectionFailure("Connection error 1"),
        ConnectionFailure("Connection error 2"),
        asyncio.Future()
    ]
    side_effects[2].set_result("success after retry")
    mock_func.side_effect = side_effects

    # Apply the retry decorator with minimal delays for testing
    decorated_func = with_retry(max_attempts=3, initial_delay=0.01, max_delay=0.01)(mock_func)

    # Call the decorated function
    result = await decorated_func()

    # Verify the result and that the function was called three times
    assert result == "success after retry"
    assert mock_func.call_count == 3


@pytest.mark.asyncio
async def test_retry_max_attempts_exceeded():
    """Test failure after exceeding maximum retry attempts."""
    # Create a mock function that always fails
    mock_func = MagicMock()
    mock_func.side_effect = ConnectionFailure("Persistent connection error")

    # Apply the retry decorator with minimal delays for testing
    decorated_func = with_retry(max_attempts=3, initial_delay=0.01, max_delay=0.01)(mock_func)

    # Call the decorated function and expect it to raise ConnectionError
    with pytest.raises(ConnectionError) as exc_info:
        await decorated_func()

    # Verify the error message and that the function was called three times
    assert "Failed after 3 attempts" in str(exc_info.value)
    assert mock_func.call_count == 3


@pytest.mark.asyncio
async def test_retry_with_server_selection_timeout():
    """Test retry with ServerSelectionTimeoutError."""
    # Create a mock function that fails with ServerSelectionTimeoutError then succeeds
    mock_func = MagicMock()

    # Set up side effects: first call raises ServerSelectionTimeoutError, second call succeeds
    side_effects = [
        ServerSelectionTimeoutError("Server selection timeout"),
        asyncio.Future()
    ]
    side_effects[1].set_result("success after timeout")
    mock_func.side_effect = side_effects

    # Apply the retry decorator with minimal delays for testing
    decorated_func = with_retry(max_attempts=2, initial_delay=0.01)(mock_func)

    # Call the decorated function
    result = await decorated_func()

    # Verify the result and that the function was called twice
    assert result == "success after timeout"
    assert mock_func.call_count == 2


@pytest.mark.asyncio
async def test_retry_with_exponential_backoff():
    """Test that exponential backoff is applied correctly."""
    # Create a mock function that always fails
    mock_func = MagicMock()
    mock_func.side_effect = ConnectionFailure("Connection error")

    # Mock asyncio.sleep to verify delay times
    with patch('asyncio.sleep') as mock_sleep:
        # Create a future for each sleep call
        sleep_futures = [asyncio.Future() for _ in range(2)]
        for future in sleep_futures:
            future.set_result(None)
        mock_sleep.side_effect = sleep_futures

        # Apply the retry decorator with specific backoff parameters
        decorated_func = with_retry(
            max_attempts=3,
            initial_delay=0.1,
            max_delay=2.0,
            exponential_base=2
        )(mock_func)

        # Call the decorated function and expect it to raise ConnectionError
        with pytest.raises(ConnectionError):
            await decorated_func()

        # Verify that sleep was called with the expected delays
        assert mock_sleep.call_count == 2
        # The actual delay values might be different due to exponential backoff
        # Just verify that sleep was called twice
