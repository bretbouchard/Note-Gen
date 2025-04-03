import pytest
from fastapi import FastAPI, APIRouter, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel
from note_gen.utils.logging_utils import (
    setup_logger, 
    log_endpoint, 
    RequestContextFilter, 
    LOGGER_NAME,
    setup_request_id_middleware
)
import uuid
from contextvars import ContextVar

# Create context variable for request ID
request_id_ctx_var = ContextVar("request_id", default="unknown")

# Create router instance
router = APIRouter()

class PatternData(BaseModel):
    name: str
    value: int

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    """Set up logging capture for all tests"""
    # Reset any existing handlers
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers = []
    
    # Set up capture at DEBUG level to ensure we catch everything
    caplog.set_level(logging.DEBUG, logger=LOGGER_NAME)
    
    # Create and configure the logger
    logger = setup_logger(LOGGER_NAME)
    logger.propagate = True  # Ensure logs propagate to root logger
    
    # Add the RequestContextFilter to caplog handler
    caplog.handler.addFilter(RequestContextFilter())
    
    return logger

@pytest.fixture
def test_client():
    """Create test client with router"""
    app = FastAPI()
    setup_request_id_middleware(app)  # Add the middleware
    app.include_router(router)
    return TestClient(app)

@router.get("/api/v1/note-patterns/")
@log_endpoint
async def test_get_patterns(request: Request):
    """Test endpoint that always returns success"""
    logger = logging.getLogger(LOGGER_NAME)
    logger.info(f"Processing GET request for note patterns")
    return JSONResponse(content={"status": "success"})

def test_request_id_consistency(test_client, caplog, setup_logging):
    """Test that request ID is consistent across the request lifecycle"""
    # Clear any existing logs
    caplog.clear()
    
    test_request_id = str(uuid.uuid4())
    
    # Make the request
    response = test_client.get(
        "/api/v1/note-patterns/",
        headers={"X-Request-ID": test_request_id}
    )
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == test_request_id
    
    # Get logs specifically from our logger
    log_records = [r for r in caplog.records if r.name == LOGGER_NAME]
    
    # Debug print the actual records
    print("\nMatching log records:")
    for record in log_records:
        print(f"Record: {record.name} - {record.getMessage()}")
    
    # Verify each log record has the correct request ID
    for record in log_records:
        assert hasattr(record, "request_id"), f"Log record missing request_id attribute: {record.__dict__}"
        assert record.request_id == test_request_id, f"Expected request_id {test_request_id}, got {record.request_id}"
