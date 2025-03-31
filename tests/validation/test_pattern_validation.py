"""Test pattern validation functionality."""
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote
from src.note_gen.core.enums import PatternType, ValidationLevel
from src.note_gen.validation.validation_manager import ValidationManager
from src.note_gen.validation.pattern_validation import PatternValidator

def test_rhythm_pattern_validation() -> None:
    """Test rhythm pattern validation."""
    # Valid pattern
    pattern = RhythmPattern(
        name="test_pattern",
        pattern=[
            RhythmNote(position=0.0, duration=1.0),
            RhythmNote(position=1.0, duration=1.0)
        ],
        pattern_type=PatternType.RHYTHMIC
    )

    result = ValidationManager.validate_pattern(pattern, ValidationLevel.NORMAL)
    assert result.is_valid
    assert not result.violations

    # For invalid pattern test, we'll need to bypass the model validation
    # and test the validation logic directly
    invalid_pattern = RhythmPattern(
        name="invalid_pattern",
        pattern=[
            RhythmNote(position=0.0, duration=1.0),  # Create in correct order first
            RhythmNote(position=1.0, duration=1.0)
        ],
        pattern_type=PatternType.RHYTHMIC
    )
    # Then modify the pattern after creation to make it invalid
    invalid_pattern.pattern[0].position = 1.0
    invalid_pattern.pattern[1].position = 0.0

    result = ValidationManager.validate_pattern(invalid_pattern, ValidationLevel.NORMAL)
    assert not result.is_valid
    assert len(result.violations) == 1
    assert result.violations[0].code == "UNORDERED_POSITIONS"

def test_validation_levels() -> None:
    """Test validation with different levels."""
    pattern = RhythmPattern(
        name="test_pattern",
        pattern=[
            RhythmNote(position=0.0, duration=1.0),
            RhythmNote(position=1.0, duration=1.0)
        ],
        pattern_type=PatternType.RHYTHMIC
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
        ],
        pattern_type=PatternType.RHYTHMIC
    )
    
    result = PatternValidator.validate(pattern)
    assert result.is_valid
    assert not result.violations
