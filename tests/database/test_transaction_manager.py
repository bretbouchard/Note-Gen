"""Tests for transaction management."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient
from note_gen.database.transaction import TransactionManager, TransactionError


@pytest.fixture
def mock_client():
    """Create a mock AsyncIOMotorClient."""
    client = MagicMock(spec=AsyncIOMotorClient)

    # Mock the session
    mock_session = AsyncMock()
    mock_session.start_transaction = MagicMock()  # Not an async method
    mock_session.commit_transaction = AsyncMock()
    mock_session.abort_transaction = AsyncMock()
    mock_session.end_session = AsyncMock()

    # Mock the start_session method to return our mock session
    client.start_session = AsyncMock(return_value=mock_session)

    # Setup __aenter__ and __aexit__ for the session
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    return client, mock_session


@pytest.mark.asyncio
async def test_transaction_manager_success(mock_client):
    """Test successful transaction execution."""
    client, mock_session = mock_client
    manager = TransactionManager(client)

    # Use the transaction manager as a context manager
    async with manager() as session:
        assert session == mock_session

    # Verify the session methods were called correctly
    client.start_session.assert_called_once()
    mock_session.start_transaction.assert_called_once()
    mock_session.commit_transaction.assert_called_once()
    mock_session.end_session.assert_called_once()
    mock_session.abort_transaction.assert_not_called()


@pytest.mark.asyncio
async def test_transaction_manager_failure(mock_client):
    """Test transaction failure and rollback."""
    client, mock_session = mock_client
    manager = TransactionManager(client)

    # Simulate an error during the transaction
    with pytest.raises(TransactionError):
        async with manager() as session:
            assert session == mock_session
            raise ValueError("Test error")

    # Verify the session methods were called correctly
    client.start_session.assert_called_once()
    mock_session.start_transaction.assert_called_once()
    mock_session.abort_transaction.assert_called_once()
    mock_session.end_session.assert_called_once()
    mock_session.commit_transaction.assert_not_called()


@pytest.mark.asyncio
async def test_run_transaction_success(mock_client):
    """Test successful execution of multiple operations in a transaction."""
    client, mock_session = mock_client
    manager = TransactionManager(client)

    # Create mock operations
    op1 = AsyncMock(return_value="result1")
    op2 = AsyncMock(return_value="result2")

    # Run the operations in a transaction
    results = await manager.run_transaction([op1, op2])

    # Verify the results
    assert results == ["result1", "result2"]

    # Verify the operations were called with the session
    op1.assert_called_once_with(session=mock_session)
    op2.assert_called_once_with(session=mock_session)

    # Verify the session methods were called correctly
    client.start_session.assert_called_once()
    mock_session.start_transaction.assert_called_once()
    mock_session.commit_transaction.assert_called_once()
    mock_session.end_session.assert_called_once()
    mock_session.abort_transaction.assert_not_called()


@pytest.mark.asyncio
async def test_run_transaction_failure(mock_client):
    """Test failure and rollback when running operations in a transaction."""
    client, mock_session = mock_client
    manager = TransactionManager(client)

    # Create a mock operation that raises an exception
    op1 = AsyncMock(side_effect=ValueError("Test error"))

    # Run the operation in a transaction and expect it to fail
    with pytest.raises(TransactionError):
        await manager.run_transaction([op1])

    # Verify the operation was called with the session
    op1.assert_called_once_with(session=mock_session)

    # Verify the session methods were called correctly
    client.start_session.assert_called_once()
    mock_session.start_transaction.assert_called_once()
    mock_session.abort_transaction.assert_called_once()
    mock_session.end_session.assert_called_once()
    mock_session.commit_transaction.assert_not_called()
