from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from ..errors import ErrorCodes

class ValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            if "content-type" not in request.headers:
                return JSONResponse(
                    status_code=400,
                    content={
                        "code": ErrorCodes.VALIDATION_ERROR.value,
                        "message": "Missing required header: content-type"
                    }
                )

        return await call_next(request)

async def validate_request_middleware(request: Request, call_next):
    middleware = ValidationMiddleware(app=None)
    return await middleware.dispatch(request, call_next)
