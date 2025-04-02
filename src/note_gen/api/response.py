from typing import Any, Optional, TypeVar, Generic
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    
    @classmethod
    def success_response(cls, data: Any = None) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "data": data}
        )
    
    @classmethod
    def error_response(
        cls, 
        message: str, 
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "error": message}
        )