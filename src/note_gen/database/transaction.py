"""Transaction management for MongoDB operations."""

from typing import Any, Callable, List, TypeVar, Awaitable, Protocol, Type
import functools
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession, AsyncIOMotorDatabase
from pymongo.errors import OperationFailure
from .exceptions import TransactionError

T = TypeVar('T')

class AsyncOperation(Protocol):
    async def __call__(self, session: AsyncIOMotorClientSession | None = None) -> Any:
        ...

class TransactionManager:
    """Manages database transactions."""
    
    def __init__(self, client: AsyncIOMotorClient[Any]) -> None:
        self.client = client
    
    async def run_transaction(self, operations: List[AsyncOperation]) -> List[Any]:
        """Run multiple operations in a transaction."""
        async with await self.client.start_session() as session:
            try:
                async with session.start_transaction():
                    results = []
                    for operation in operations:
                        result = await operation(session=session)
                        results.append(result)
                    return results
            except OperationFailure as e:
                await session.abort_transaction()
                raise TransactionError(f"Transaction failed: {str(e)}")

def transactional(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """Decorator to make a function run in a transaction."""
    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, session: AsyncIOMotorClientSession | None = None, **kwargs: Any) -> T:
        if session:
            return await func(self, *args, session=session, **kwargs)
        
        async with await self.client.start_session() as new_session:
            async with new_session.start_transaction():
                try:
                    result = await func(self, *args, session=new_session, **kwargs)
                    return result
                except Exception as e:
                    await new_session.abort_transaction()
                    raise TransactionError(f"Transaction failed: {str(e)}")
    
    return wrapper

async def with_transaction(
    client: AsyncIOMotorClient[Any],
    operation: Callable[..., Awaitable[T]]
) -> T:
    """Execute operation within a transaction."""
    async with await client.start_session() as session:
        try:
            async with session.start_transaction():
                return await operation(session=session)
        except OperationFailure as e:
            await session.abort_transaction()
            raise TransactionError(f"Transaction failed: {str(e)}")
