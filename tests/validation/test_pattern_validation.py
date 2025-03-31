"""Tests for pattern validation."""
import pytest
from src.note_gen.core.enums import ValidationLevel
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.models.rhythm_note import RhythmNote
from src.note_gen.validation.pattern_validation import PatternValidator
from src.note_gen.validation.validation_manager import ValidationManager

def test_rhythm_pattern_validation() -> None:
    """Test rhythm pattern validation."""
    # Valid pattern
    pattern = RhythmPattern(
        name="test_pattern",
        pattern=[
            RhythmNote(position=0.0, duration=1.0),
            RhythmNote(position=1.0, duration=1.0)
        ]
    )
    
    result = ValidationManager.validate_pattern(pattern)
    assert result.is_valid
    assert not result.violations

    # Invalid pattern (unordered positions)
    invalid_pattern = RhythmPattern(
        name="invalid_pattern",
        pattern=[
            RhythmNote(position=1.0, duration=1.0),
            RhythmNote(position=0.0, duration=1.0)
        ]
    )
    
    result = ValidationManager.validate_pattern(invalid_pattern)
    assert not result.is_valid
    assert len(result.violations) > 0

def test_validation_levels() -> None:
    """Test validation with different levels."""
    pattern = RhythmPattern(
        name="test_pattern",
        pattern=[
            RhythmNote(position=0.0, duration=1.0),
            RhythmNote(position=1.0, duration=1.0)
        ]
    )
    
    # Relaxed validation
    result = ValidationManager.validate_pattern(pattern, ValidationLevel.RELAXED)
    assert result.is_valid

    # Normal validation
    result = ValidationManager.validate_pattern(pattern, ValidationLevel.NORMAL)
    assert result.is_valid

    # Strict validation
    result = ValidationManager.validate_pattern(pattern, ValidationLevel.STRICT)
    assert result.is_valid

def test_pattern_validator_direct() -> None:
    """Test PatternValidator directly."""
    pattern = RhythmPattern(
        name="test_pattern",
        pattern=[
            RhythmNote(position=0.0, duration=1.0),
            RhythmNote(position=1.0, duration=1.0)
        ]
    )
    
    result = PatternValidator.validate(pattern)
    assert result.is_valid
    assert not result.violations