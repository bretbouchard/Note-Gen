"""Tests for data models."""
import pytest
from unittest.mock import patch, MagicMock
from note_gen.models.data import DataStore, PatternData
from note_gen.core.enums import ScaleType, ValidationLevel
from note_gen.validation.base_validation import ValidationResult, ValidationViolation


def test_data_store_init():
    """Test DataStore initialization."""
    store = DataStore()
    assert store.patterns == {}


@patch('note_gen.models.data.RHYTHM_PATTERNS', {'test_rhythm': {}})
@patch('note_gen.models.data.NOTE_PATTERNS', {'test_note': {}})
@patch('note_gen.models.data.COMMON_PROGRESSIONS', {'test_progression': {}})
@patch('note_gen.models.data.SCALE_INTERVALS', {ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]})
@patch('note_gen.models.data.VALID_KEYS', ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
def test_pattern_data_valid():
    """Test PatternData with valid data."""
    # Create a valid pattern data
    pattern = PatternData(
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


@patch('src.note_gen.models.data.RHYTHM_PATTERNS', {'test_rhythm': {}})
@patch('src.note_gen.models.data.NOTE_PATTERNS', {'test_note': {}})
@patch('src.note_gen.models.data.COMMON_PROGRESSIONS', {'test_progression': {}})
@patch('src.note_gen.models.data.SCALE_INTERVALS', {ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]})
@patch('src.note_gen.models.data.VALID_KEYS', ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
def test_pattern_data_invalid_rhythm():
    """Test PatternData with invalid rhythm pattern."""
    # Attempt to create with invalid rhythm pattern
    with pytest.raises(ValueError, match="Invalid rhythm pattern"):
        PatternData(
            name="Test Pattern",
            rhythm_pattern="invalid_rhythm",
            note_pattern="test_note",
            progression="test_progression",
            scale_type=ScaleType.MAJOR,
            key="C"
        )


@patch('note_gen.models.data.RHYTHM_PATTERNS', {'test_rhythm': {}})
@patch('note_gen.models.data.NOTE_PATTERNS', {'test_note': {}})
@patch('note_gen.models.data.COMMON_PROGRESSIONS', {'test_progression': {}})
@patch('note_gen.models.data.SCALE_INTERVALS', {ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]})
@patch('note_gen.models.data.VALID_KEYS', ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
def test_pattern_data_invalid_note():
    """Test PatternData with invalid note pattern."""
    # Attempt to create with invalid note pattern
    with pytest.raises(ValueError, match="Invalid note pattern"):
        PatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="invalid_note",
            progression="test_progression",
            scale_type=ScaleType.MAJOR,
            key="C"
        )


@patch('note_gen.models.data.RHYTHM_PATTERNS', {'test_rhythm': {}})
@patch('note_gen.models.data.NOTE_PATTERNS', {'test_note': {}})
@patch('note_gen.models.data.COMMON_PROGRESSIONS', {'test_progression': {}})
@patch('note_gen.models.data.SCALE_INTERVALS', {ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]})
@patch('note_gen.models.data.VALID_KEYS', ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
def test_pattern_data_invalid_progression():
    """Test PatternData with invalid progression."""
    # Attempt to create with invalid progression
    with pytest.raises(ValueError, match="Invalid progression"):
        PatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="test_note",
            progression="invalid_progression",
            scale_type=ScaleType.MAJOR,
            key="C"
        )


@patch('note_gen.models.data.RHYTHM_PATTERNS', {'test_rhythm': {}})
@patch('note_gen.models.data.NOTE_PATTERNS', {'test_note': {}})
@patch('note_gen.models.data.COMMON_PROGRESSIONS', {'test_progression': {}})
@patch('note_gen.models.data.SCALE_INTERVALS', {ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]})
@patch('note_gen.models.data.VALID_KEYS', ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
def test_pattern_data_invalid_scale_type():
    """Test PatternData with invalid scale type."""
    # Attempt to create with invalid scale type
    with pytest.raises(ValueError, match="Invalid scale type"):
        PatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="test_note",
            progression="test_progression",
            scale_type=ScaleType.MELODIC_MINOR,  # Not in SCALE_INTERVALS
            key="C"
        )


@patch('note_gen.models.data.RHYTHM_PATTERNS', {'test_rhythm': {}})
@patch('note_gen.models.data.NOTE_PATTERNS', {'test_note': {}})
@patch('note_gen.models.data.COMMON_PROGRESSIONS', {'test_progression': {}})
@patch('note_gen.models.data.SCALE_INTERVALS', {ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]})
@patch('note_gen.models.data.VALID_KEYS', ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
def test_pattern_data_invalid_key():
    """Test PatternData with invalid key."""
    # Attempt to create with invalid key
    with pytest.raises(ValueError, match="Invalid key"):
        PatternData(
            name="Test Pattern",
            rhythm_pattern="test_rhythm",
            note_pattern="test_note",
            progression="test_progression",
            scale_type=ScaleType.MAJOR,
            key="H"  # Not a valid key
        )


@patch('note_gen.models.data.RHYTHM_PATTERNS', {'test_rhythm': {}})
@patch('note_gen.models.data.NOTE_PATTERNS', {'test_note': {}})
@patch('note_gen.models.data.COMMON_PROGRESSIONS', {'test_progression': {}})
@patch('note_gen.models.data.SCALE_INTERVALS', {ScaleType.MAJOR: [0, 2, 4, 5, 7, 9, 11]})
@patch('note_gen.models.data.VALID_KEYS', ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
@patch('note_gen.models.data.validate_pattern_structure')
def test_validate_rhythm(mock_validate):
    """Test validate_rhythm method."""
    # Mock the validation result
    mock_result = ValidationResult(is_valid=True)
    mock_validate.return_value = []

    # Create a pattern data
    pattern = PatternData(
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
    assert result.is_valid is True
    mock_validate.assert_called_once()
