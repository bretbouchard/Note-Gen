"""Tests for database transaction management."""

import pytest
from src.note_gen.database.exceptions import TransactionError

async def test_transaction_success(transaction_manager):
    """Test successful transaction execution."""
    async def operation1(session=None):
        return "result1"
    
    async def operation2(session=None):
        return "result2"
    
    results = await transaction_manager.run_transaction([operation1, operation2])
    assert results == ["result1", "result2"]

async def test_transaction_rollback(transaction_manager):
    """Test transaction rollback on error."""
    async def operation1(session=None):
        return "result1"
    
    async def operation2(session=None):
        raise ValueError("Test error")
    
    with pytest.raises(TransactionError):
        await transaction_manager.run_transaction([operation1, operation2])

async def test_transaction_decorator(mongodb_client):
    """Test the transactional decorator."""
    from src.note_gen.database.transaction import transactional
    
    class TestRepo:
        def __init__(self, client):
            self.client = client
        
        @transactional
        async def test_operation(self, value, session=None):
            return value
    
    repo = TestRepo(mongodb_client)
    result = await repo.test_operation("test_value")
    assert result == "test_value"
