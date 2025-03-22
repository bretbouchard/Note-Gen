from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, data: T) -> 'APIResponse[T]':
        return cls(success=True, data=data)
    
    @classmethod
    def error(cls, message: str) -> 'APIResponse[T]':
        return cls(success=False, error=message)