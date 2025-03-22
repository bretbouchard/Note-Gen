import asyncio
from functools import wraps
from typing import TypeVar, Callable, Any
from .errors import DatabaseError, ConnectionError
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

T = TypeVar('T')
logger = logging.getLogger(__name__)

def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 0.1,
    max_delay: float = 2.0,
    exponential_base: float = 2
) -> Callable:
    """Decorator for retrying database operations."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_error = None
            delay = initial_delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                    last_error = e
                    if attempt == max_attempts - 1:
                        raise ConnectionError(f"Failed after {max_attempts} attempts: {str(e)}")
                    
                    delay = min(delay * exponential_base, max_delay)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                    
            raise last_error  # Should never reach here

        return wrapper
    return decorator