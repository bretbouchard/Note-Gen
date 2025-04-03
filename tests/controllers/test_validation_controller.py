"""Tests for the validation controller."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from note_gen.controllers.validation_controller import ValidationController
from note_gen.core.enums import ValidationLevel, ScaleType, PatternDirection
from note_gen.validation.base_validation import ValidationResult, ValidationViolation
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.note_sequence import NoteSequence
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.note import Note


@pytest.fixture
def controller():
    """Create a validation controller instance."""
    return ValidationController()


@pytest.fixture
def sample_note_pattern():
    """Create a sample note pattern."""
    return NotePattern(
        id="507f1f77bcf86cd799439011",
        name="Test Pattern",
        complexity=3.0,
        tags=["test", "pattern"],
        data=NotePatternData(
            notes=[Note(pitch=60, duration=1.0, velocity=100)],
            scale_type=ScaleType.MAJOR,
            direction=PatternDirection.ASCENDING
        )
    )


@pytest.fixture
def sample_rhythm_pattern():
    """Create a sample rhythm pattern."""
    return RhythmPattern(
        id="507f1f77bcf86cd799439012",
        name="Test Rhythm",
        time_signature=[4, 4],
        notes=[RhythmNote(position=0, duration=1.0, velocity=100)]
    )


@pytest.fixture
def sample_chord_progression():
    """Create a sample chord progression."""
    return ChordProgression(
        id="507f1f77bcf86cd799439013",
        name="Test Progression",
        key="C",
        scale_type="MAJOR",
        chords=[]
    )


@pytest.mark.asyncio
async def test_create():
    """Test the create factory method."""
    controller = await ValidationController.create()
    assert isinstance(controller, ValidationController)
    assert controller.validation_manager is not None


@pytest.mark.asyncio
async def test_validate_note_pattern(controller, sample_note_pattern):
    """Test validating a note pattern."""
    # Mock the validation manager
    controller.validation_manager.validate = MagicMock(
        return_value=ValidationResult(is_valid=True, violations=[])
    )
    
    # Test with model instance
    result = await controller.validate_note_pattern(sample_note_pattern)
    assert result.is_valid is True
    assert len(result.violations) == 0
    
    # Test with dictionary
    pattern_dict = sample_note_pattern.model_dump()
    result = await controller.validate_note_pattern(pattern_dict)
    assert result.is_valid is True
    assert len(result.violations) == 0


@pytest.mark.asyncio
async def test_validate_note_pattern_invalid_dict(controller):
    """Test validating an invalid note pattern dictionary."""
    # Test with invalid dictionary
    invalid_dict = {"name": "Invalid Pattern"}  # Missing required fields
    result = await controller.validate_note_pattern(invalid_dict)
    assert result.is_valid is False
    assert len(result.violations) == 1
    assert "Invalid note pattern format" in result.violations[0].message


@pytest.mark.asyncio
async def test_validate_rhythm_pattern(controller, sample_rhythm_pattern):
    """Test validating a rhythm pattern."""
    # Mock the validation manager
    controller.validation_manager.validate = MagicMock(
        return_value=ValidationResult(is_valid=True, violations=[])
    )
    
    # Test with model instance
    result = await controller.validate_rhythm_pattern(sample_rhythm_pattern)
    assert result.is_valid is True
    assert len(result.violations) == 0
    
    # Test with dictionary
    pattern_dict = sample_rhythm_pattern.model_dump()
    result = await controller.validate_rhythm_pattern(pattern_dict)
    assert result.is_valid is True
    assert len(result.violations) == 0


@pytest.mark.asyncio
async def test_validate_rhythm_pattern_invalid_dict(controller):
    """Test validating an invalid rhythm pattern dictionary."""
    # Test with invalid dictionary
    invalid_dict = {"name": "Invalid Rhythm"}  # Missing required fields
    result = await controller.validate_rhythm_pattern(invalid_dict)
    assert result.is_valid is False
    assert len(result.violations) == 1
    assert "Invalid rhythm pattern format" in result.violations[0].message


@pytest.mark.asyncio
async def test_validate_chord_progression(controller, sample_chord_progression):
    """Test validating a chord progression."""
    # Mock the validation manager
    controller.validation_manager.validate = MagicMock(
        return_value=ValidationResult(is_valid=True, violations=[])
    )
    
    # Test with model instance
    result = await controller.validate_chord_progression(sample_chord_progression)
    assert result.is_valid is True
    assert len(result.violations) == 0
    
    # Test with dictionary
    progression_dict = sample_chord_progression.model_dump()
    result = await controller.validate_chord_progression(progression_dict)
    assert result.is_valid is True
    assert len(result.violations) == 0


@pytest.mark.asyncio
async def test_validate_chord_progression_invalid_dict(controller):
    """Test validating an invalid chord progression dictionary."""
    # Test with invalid dictionary
    invalid_dict = {"name": "Invalid Progression"}  # Missing required fields
    result = await controller.validate_chord_progression(invalid_dict)
    assert result.is_valid is False
    assert len(result.violations) == 1
    assert "Invalid chord progression format" in result.violations[0].message


@pytest.mark.asyncio
async def test_validate_config(controller):
    """Test validating a configuration."""
    # Mock the validation manager
    controller.validation_manager.validate_config = MagicMock(return_value=True)
    
    # Test with valid config
    config = {"key": "value"}
    result = await controller.validate_config(config, "test_config")
    assert result is True
    controller.validation_manager.validate_config.assert_called_once_with(config, "test_config")
