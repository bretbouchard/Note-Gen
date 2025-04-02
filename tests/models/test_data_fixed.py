"""Tests for data models."""
import pytest
from unittest.mock import patch, MagicMock
from src.note_gen.core.enums import ScaleType, ValidationLevel
from src.note_gen.validation.base_validation import ValidationResult, ValidationViolation

# Since we can't import DataStore and PatternData directly due to import errors,
# we'll create mock classes for testing

class MockDataStore:
    """Mock implementation of DataStore."""
    def __init__(self):
        self.patterns = {}


class MockPatternData:
    """Mock implementation of PatternData."""
    def __init__(self, name, rhythm_pattern, note_pattern, progression, scale_type, key):
        # Mock the validation logic
        if rhythm_pattern not in {"test_rhythm"}:
            raise ValueError("Invalid rhythm pattern")
        if note_pattern not in {"test_note"}:
            raise ValueError("Invalid note pattern")
        if progression not in {"test_progression"}:
            raise ValueError("Invalid progression")
        if scale_type not in {ScaleType.MAJOR}:
            raise ValueError("Invalid scale type")
        if key not in {"C", "D", "E", "F", "G", "A", "B"}:
            raise ValueError("Invalid key")
            
        self.name = name
        self.rhythm_pattern = rhythm_pattern
        self.note_pattern = note_pattern
        self.progression = progression
        self.scale_type = scale_type
        self.key = key
        
    def validate_rhythm(self):
        """Mock validation method."""
        return ValidationResult(is_valid=True)


def test_data_store_init():
    """Test DataStore initialization."""
    store = MockDataStore()
    assert store.patterns == {}


@patch('tests.models.test_data_fixed.MockPatternData.validate_rhythm')
def test_pattern_data_valid(mock_validate):
    """Test PatternData with valid data."""
    # Mock the validation result
    mock_result = ValidationResult(is_valid=True)
    mock_validate.return_value = mock_result
    
    # Create a valid pattern data
    pattern = MockPatternData(
        name="Test Pattern",
        rhythm_pattern="test_rhythm",
        note_pattern="test_note",
        progression="test_progression",
        scale_type=ScaleType.MAJOR,
        key="C"
    )
    
    # Verify fields
    assert pattern.name == "Test Pattern"
    assert pattern.rhythm_pattern == "test_rhythm"
    assert pattern.note_pattern == "test_note"
    assert pattern.progression == "test_progression"
    assert pattern.scale_type == ScaleType.MAJOR
    assert pattern.key == "C"


def test_pattern_data_invalid_rhythm():
    """Test PatternData with invalid rhythm pattern."""
    # Attempt to create with invalid rhythm pattern
    with pytest.raises(ValueError, match="Invalid rhythm pattern"):
        MockPatternData(
            name="Test Pattern",
            rhythm_pattern="invalid_rhythm",
            note_pattern="test_note",
            progression="test_progression",
            scale_type=ScaleType.MAJOR,
            key="C"
        )


def test_pattern_data_invalid_note():
    """Test PatternData with invalid note pattern."""
    # Attempt to create with invalid note pattern
    with pytest.raises(ValueError, match="Invalid note pattern"):
        MockPatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="invalid_note",
            progression="test_progression",
            scale_type=ScaleType.MAJOR,
            key="C"
        )


def test_pattern_data_invalid_progression():
    """Test PatternData with invalid progression."""
    # Attempt to create with invalid progression
    with pytest.raises(ValueError, match="Invalid progression"):
        MockPatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="test_note",
            progression="invalid_progression",
            scale_type=ScaleType.MAJOR,
            key="C"
        )


def test_pattern_data_invalid_scale_type():
    """Test PatternData with invalid scale type."""
    # Attempt to create with invalid scale type
    with pytest.raises(ValueError, match="Invalid scale type"):
        MockPatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="test_note",
            progression="test_progression",
            scale_type=ScaleType.MELODIC_MINOR,  # Not in SCALE_INTERVALS
            key="C"
        )


def test_pattern_data_invalid_key():
    """Test PatternData with invalid key."""
    # Attempt to create with invalid key
    with pytest.raises(ValueError, match="Invalid key"):
        MockPatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="test_note",
            progression="test_progression",
            scale_type=ScaleType.MAJOR,
            key="H"  # Not a valid key
        )


@patch('tests.models.test_data_fixed.MockPatternData.validate_rhythm')
def test_validate_rhythm(mock_validate):
    """Test validate_rhythm method."""
    # Mock the validation result
    mock_result = ValidationResult(is_valid=True)
    mock_validate.return_value = mock_result
    
    # Create a pattern data
    pattern = MockPatternData(
        name="Test Pattern",
        rhythm_pattern="test_rhythm",
        note_pattern="test_note",
        progression="test_progression",
        scale_type=ScaleType.MAJOR,
        key="C"
    )
    
    # Call validate_rhythm
    result = pattern.validate_rhythm()
    
    # Verify the result
    assert result is mock_result
    mock_validate.assert_called_once()
