from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from ..errors import ErrorCodes
from ...database.errors import ConnectionError, DocumentNotFoundError
import logging

logger = logging.getLogger(__name__)

def setup_error_handlers(app: FastAPI) -> None:
    """Register error handlers with the FastAPI app.

    Note: The handler functions and their parameters are used by FastAPI's
    exception handler system, even though they appear unused to static analyzers.
    """

    @app.exception_handler(ConnectionError)
    async def database_error_handler(request: Request, exc: ConnectionError) -> JSONResponse:  # noqa: F841
        """Handle database connection errors"""
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCodes.DATABASE_ERROR.value,
                "message": f"Database error: {str(exc)}"
            }
        )

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(request: Request, exc: DocumentNotFoundError) -> JSONResponse:  # noqa: F841
        """Handle document not found errors"""
        return JSONResponse(
            status_code=404,
            content={
                "code": ErrorCodes.NOT_FOUND.value,
                "message": str(exc)
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # noqa: F841
        """Handle validation errors"""
        return JSONResponse(
            status_code=422,
            content={
                "code": ErrorCodes.VALIDATION_ERROR.value,
                "message": "Validation error",
                "details": exc.errors()
            }
        )