"""
API package initialization.
This package should contain API-related utilities, not routes.
"""

from .errors import APIException, ErrorCodes

__all__ = ['APIException', 'ErrorCodes']