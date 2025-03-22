from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def success_response(cls, data: T) -> 'APIResponse[T]':
        return cls(success=True, data=data)

    @classmethod
    def error_response(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> 'APIResponse[T]':
        return cls(
            success=False,
            error={
                "code": code,
                "message": message,
                "details": details
            }
        )