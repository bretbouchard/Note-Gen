"""Tests for validation models."""
import pytest
from note_gen.models.validation import (
    ValidationError,
    ValidationViolation,
    ValidationResult
)


def test_validation_error_init():
    """Test ValidationError initialization."""
    # Create a validation error
    error = ValidationError(
        field="username",
        message="Username is required"
    )
    
    # Verify fields
    assert error.field == "username"
    assert error.message == "Username is required"
    assert error.code == "VALIDATION_ERROR"  # Default value


def test_validation_error_custom_code():
    """Test ValidationError with custom code."""
    # Create a validation error with custom code
    error = ValidationError(
        field="email",
        message="Invalid email format",
        code="INVALID_FORMAT"
    )
    
    # Verify custom code
    assert error.code == "INVALID_FORMAT"


def test_validation_violation_init():
    """Test ValidationViolation initialization."""
    # Create a validation violation
    violation = ValidationViolation(
        code="REQUIRED_FIELD",
        message="Field is required"
    )
    
    # Verify fields
    assert violation.code == "REQUIRED_FIELD"
    assert violation.message == "Field is required"
    assert violation.path == ""  # Default value
    assert violation.details == {}  # Default value


def test_validation_violation_with_path():
    """Test ValidationViolation with path."""
    # Create a validation violation with path
    violation = ValidationViolation(
        code="INVALID_FORMAT",
        message="Invalid format",
        path="user.email"
    )
    
    # Verify path
    assert violation.path == "user.email"


def test_validation_violation_with_details():
    """Test ValidationViolation with details."""
    # Create a validation violation with details
    violation = ValidationViolation(
        code="INVALID_VALUE",
        message="Invalid value",
        details={"expected": "string", "received": "integer"}
    )
    
    # Verify details
    assert violation.details == {"expected": "string", "received": "integer"}


def test_validation_result_init():
    """Test ValidationResult initialization."""
    # Create a validation result
    result = ValidationResult(
        is_valid=True
    )
    
    # Verify fields
    assert result.is_valid is True
    assert result.violations == []  # Default value


def test_validation_result_with_violations():
    """Test ValidationResult with violations."""
    # Create violations
    violations = [
        ValidationViolation(code="ERROR1", message="Error 1"),
        ValidationViolation(code="ERROR2", message="Error 2")
    ]
    
    # Create a validation result with violations
    result = ValidationResult(
        is_valid=False,
        violations=violations
    )
    
    # Verify fields
    assert result.is_valid is False
    assert len(result.violations) == 2
    assert result.violations[0].code == "ERROR1"
    assert result.violations[1].code == "ERROR2"


def test_validation_result_add_violation():
    """Test adding a violation to a ValidationResult."""
    # Create a validation result
    result = ValidationResult(is_valid=True)
    
    # Create a violation
    violation = ValidationViolation(code="ERROR", message="Error")
    
    # Add the violation
    result.violations.append(violation)
    result.is_valid = False
    
    # Verify the violation was added
    assert result.is_valid is False
    assert len(result.violations) == 1
    assert result.violations[0].code == "ERROR"
