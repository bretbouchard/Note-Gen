from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from starlette.responses import Response
from ..errors import ErrorCodes

class ValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
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

async def validate_request_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Standalone middleware function for validation"""
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
