"""Test error handling in the API."""

import pytest
from fastapi.testclient import TestClient
from src.note_gen.api.errors import APIException, ErrorCodes
from src.note_gen.database.errors import (
    DatabaseError,
    DocumentNotFoundError,
    ConnectionError,
    QueryError
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_exception_handling(async_client):
    """Test that API exceptions are handled correctly."""
    response = async_client.get("/api/v1/chord-progressions/nonexistent_id")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == ErrorCodes.NOT_FOUND.value
    assert "message" in data

def test_database_error_handling(async_client):
    """Test that database errors are handled correctly."""
    response = async_client.get("/api/v1/chord-progressions")
    assert response.status_code == 500
    data = response.json()
    assert data["code"] == ErrorCodes.DATABASE_ERROR.value
    assert "database" in data["message"].lower()

def test_document_not_found_handling(async_client):
    """Test handling of DocumentNotFoundError."""
    doc_id = "nonexistent_id"
    response = async_client.get(f"/api/v1/chord-progressions/{doc_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == ErrorCodes.NOT_FOUND.value
    assert "not found" in data["message"].lower()

def test_validation_error_handling(async_client):
    """Test that validation errors are handled correctly."""
    invalid_data = {
        "name": "Test Progression",
        "chords": None  # Invalid type for list field
    }
    response = async_client.post("/api/v1/chord-progressions", json=invalid_data)
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == ErrorCodes.VALIDATION_ERROR.value
    assert "validation" in data["message"].lower()
