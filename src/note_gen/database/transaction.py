"""Transaction management for MongoDB operations."""

from typing import Any, List, AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession
from contextlib import asynccontextmanager

class TransactionError(Exception):
    """Custom exception for transaction failures."""
    pass

class TransactionManager:
    """Manages database transactions."""

    def __init__(self, client: AsyncIOMotorClient) -> None:
        self.client = client

    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[AsyncIOMotorClientSession, None]:
        """Context manager for transactions."""
        session = await self.client.start_session()
        try:
            session.start_transaction()
            try:
                yield session
                await session.commit_transaction()
            except Exception as e:
                await session.abort_transaction()
                raise TransactionError(f"Transaction failed: {str(e)}")
        finally:
            await session.end_session()

    async def run_transaction(self, operations: List[Any]) -> List[Any]:
        """Run multiple operations in a transaction."""
        session = await self.client.start_session()
        try:
            session.start_transaction()
            try:
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
