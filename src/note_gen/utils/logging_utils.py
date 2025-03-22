from functools import wraps
import logging
import uuid
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import FastAPI
import time

request_id_ctx_var: ContextVar[str] = ContextVar('request_id', default='unknown')

# Create a single logger instance for the module
LOGGER_NAME = "test_logging"

class RequestContextFilter(logging.Filter):
    """Add request context to log records"""
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = request_id_ctx_var.get()
        return True

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = request_id_ctx_var.set(request_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx_var.reset(token)

def setup_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """Set up a logger with the request context filter"""
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Add new handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Add the filter
    logger.addFilter(RequestContextFilter())
    
    # Ensure propagation is enabled for pytest capture
    logger.propagate = True
    
    # Set level to DEBUG to ensure we catch everything during tests
    logger.setLevel(logging.DEBUG)
    
    return logger

def log_endpoint(func):
    """Decorator to log request information"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = next((arg for arg in args if isinstance(arg, Request)), None)
        if not request:
            return await func(*args, **kwargs)
        
        logger = setup_logger(LOGGER_NAME)
        start_time = time.time()
        
        try:
            logger.info(f"Request started: {request.method} {request.url.path}")
            response = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Request completed: {request.method} {request.url.path} - Duration: {duration:.3f}s")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    return wrapper

def setup_request_id_middleware(app: FastAPI) -> None:
    """Add RequestIDMiddleware to FastAPI application"""
    app.add_middleware(RequestIDMiddleware)
