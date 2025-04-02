"""Transaction management for MongoDB operations."""

from typing import Any, List, AsyncContextManager
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
from contextlib import asynccontextmanager

class TransactionError(Exception):
    """Custom exception for transaction failures."""
    pass

class TransactionManager:
    """Manages database transactions."""
    
    def __init__(self, client: AsyncIOMotorClient) -> None:
        self.client = client
    
    @asynccontextmanager
    async def __call__(self) -> AsyncContextManager:
        """Context manager for transactions."""
        async with await self.client.start_session() as session:
            try:
                async with session.start_transaction():
                    yield session
                    await session.commit_transaction()
            except Exception as e:
                await session.abort_transaction()
                raise TransactionError(f"Transaction failed: {str(e)}")
            finally:
                await session.end_session()

    async def run_transaction(self, operations: List[Any]) -> List[Any]:
        """Run multiple operations in a transaction."""
        async with await self.client.start_session() as session:
            try:
                async with session.start_transaction():
                    results = []
                    for operation in operations:
                        result = await operation(session=session)
                        results.append(result)
                    await session.commit_transaction()
                    return results
            except Exception as e:
                await session.abort_transaction()
                raise TransactionError(f"Transaction failed: {str(e)}")
            finally:
                await session.end_session()

# Create a singleton instance
transaction_manager = TransactionManager
