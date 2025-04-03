"""Tests for API response models."""
import pytest
from fastapi import status
from fastapi.responses import JSONResponse
from note_gen.api.models import APIResponse as ModelsAPIResponse
from note_gen.api.response import APIResponse as ResponseAPIResponse
from note_gen.api.responses import APIResponse as ResponsesAPIResponse


class TestModelsAPIResponse:
    """Tests for the APIResponse class in models.py."""

    def test_init(self):
        """Test initialization."""
        # Create a response
        response = ModelsAPIResponse(success=True, data={"key": "value"})

        # Verify fields
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error is None

    def test_success_response(self):
        """Test success_response class method."""
        # Create a success response
        response = ModelsAPIResponse.success_response(data={"key": "value"})

        # Verify fields
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error is None

    def test_error_response(self):
        """Test error_response class method."""
        # Create an error response
        response = ModelsAPIResponse.error_response(
            code="ERROR_CODE",
            message="Error message",
            details={"detail": "value"}
        )

        # Verify fields
        assert response.success is False
        assert response.data is None
        assert response.error is not None
        assert response.error["code"] == "ERROR_CODE"
        assert response.error["message"] == "Error message"
        assert response.error["details"] == {"detail": "value"}


class TestResponseAPIResponse:
    """Tests for the APIResponse class in response.py."""

    def test_init(self):
        """Test initialization."""
        # Create a response
        response = ResponseAPIResponse(success=True, data={"key": "value"})

        # Verify fields
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error is None

    def test_success_response(self):
        """Test success_response class method."""
        # Create a success response
        response = ResponseAPIResponse.success_response(data={"key": "value"})

        # Verify it's a JSONResponse
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK

        # Verify content
        content = response.body.decode()
        assert '"success":true' in content
        assert '"data":{"key":"value"}' in content

    def test_error_response(self):
        """Test error_response class method."""
        # Create an error response
        response = ResponseAPIResponse.error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Error message"
        )

        # Verify it's a JSONResponse
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify content
        content = response.body.decode()
        assert '"success":false' in content
        assert '"error":"Error message"' in content


class TestResponsesAPIResponse:
    """Tests for the APIResponse class in responses.py."""

    def test_init(self):
        """Test initialization."""
        # Create a response
        response = ResponsesAPIResponse(success=True, data={"key": "value"})

        # Verify fields
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error_message is None

    def test_ok(self):
        """Test ok class method."""
        # Create a success response
        response = ResponsesAPIResponse.ok(data={"key": "value"})

        # Verify fields
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error_message is None

    def test_error(self):
        """Test error class method."""
        # Create an error response
        response = ResponsesAPIResponse.error(message="Error message")

        # Verify fields
        assert response.success is False
        assert response.data is None
        assert response.error_message == "Error message"
