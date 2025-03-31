from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Dict, List, Tuple, Callable
import time
from ..errors import ErrorCodes
from ...core.constants import RATE_LIMIT

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.window_size = 60  # 1 minute window
        
    def _cleanup_old_requests(self, client_id: str) -> None:
        current_time = time.time()
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < self.window_size
            ]

    def is_rate_limited(self, client_id: str) -> Tuple[bool, int]:
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        self._cleanup_old_requests(client_id)
        
        # Add the new request time before checking
        self.requests[client_id].append(current_time)
        request_count = len(self.requests[client_id])
        
        # Check if we're over the limit
        if request_count > RATE_LIMIT["times"]:
            return True, request_count
            
        return False, request_count

    def clear(self) -> None:
        """Clear all stored requests - useful for testing"""
        self.requests.clear()

rate_limiter = RateLimiter()

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for validation errors
        try:
            # Attempt to parse the request body first for POST requests
            if request.method == "POST":
                await request.json()
        except ValueError:
            return JSONResponse(
                status_code=422,
                content={
                    "code": ErrorCodes.VALIDATION_ERROR.value,
                    "message": "Invalid JSON data"
                }
            )

        # Safely get client IP address
        client_id = request.client.host if request.client else "unknown"
        is_limited, count = rate_limiter.is_rate_limited(client_id)
        
        if is_limited:
            return JSONResponse(
                status_code=429,
                content={
                    "code": ErrorCodes.RATE_LIMIT_EXCEEDED.value,
                    "message": "Rate limit exceeded. Maximum 100 requests per minute allowed.",
                    "current_count": count
                }
            )

        return await call_next(request)

# Export for testing
rate_limit_store = rate_limiter.requests
