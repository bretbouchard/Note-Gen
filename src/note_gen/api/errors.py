from enum import Enum

class ErrorCodes(str, Enum):
    """Error codes for API responses."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

class APIException(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, code: ErrorCodes):
        self.message = message
        self.code = code
        super().__init__(message)
