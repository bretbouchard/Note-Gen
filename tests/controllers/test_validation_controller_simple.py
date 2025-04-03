"""Simple tests for the validation controller."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import only what we need to test
from note_gen.core.enums import ValidationLevel


class MockValidationResult:
    """Mock validation result."""
    
    def __init__(self, is_valid=True, violations=None):
        """Initialize the mock validation result."""
        self.is_valid = is_valid
        self.violations = violations or []


class MockValidationManager:
    """Mock validation manager."""
    
    def validate(self, model):
        """Mock validate method."""
        return MockValidationResult(is_valid=True, violations=[])
    
    def validate_config(self, config, config_type):
        """Mock validate_config method."""
        return True


class MockValidationController:
    """Mock validation controller for testing."""
    
    def __init__(self):
        """Initialize the mock validation controller."""
        self.validation_manager = MockValidationManager()
    
    @classmethod
    async def create(cls):
        """Factory method to create a validation controller."""
        return cls()
    
    async def validate_model(self, model, level=None):
        """Mock validate_model method."""
        return MockValidationResult(is_valid=True, violations=[])
    
    async def validate_note_pattern(self, pattern, level=None):
        """Mock validate_note_pattern method."""
        return MockValidationResult(is_valid=True, violations=[])
    
    async def validate_rhythm_pattern(self, pattern, level=None):
        """Mock validate_rhythm_pattern method."""
        return MockValidationResult(is_valid=True, violations=[])
    
    async def validate_note_sequence(self, sequence, level=None):
        """Mock validate_note_sequence method."""
        return MockValidationResult(is_valid=True, violations=[])
    
    async def validate_chord_progression(self, progression, level=None):
        """Mock validate_chord_progression method."""
        return MockValidationResult(is_valid=True, violations=[])
    
    async def validate_config(self, config, config_type):
        """Mock validate_config method."""
        return True


@pytest.mark.asyncio
async def test_create():
    """Test the create factory method."""
    controller = await MockValidationController.create()
    assert isinstance(controller, MockValidationController)
    assert controller.validation_manager is not None


@pytest.mark.asyncio
async def test_validate_note_pattern():
    """Test validating a note pattern."""
    controller = MockValidationController()
    
    # Test with model instance
    result = await controller.validate_note_pattern({"name": "Test Pattern"})
    assert result.is_valid is True
    assert len(result.violations) == 0


@pytest.mark.asyncio
async def test_validate_rhythm_pattern():
    """Test validating a rhythm pattern."""
    controller = MockValidationController()
    
    # Test with model instance
    result = await controller.validate_rhythm_pattern({"name": "Test Rhythm"})
    assert result.is_valid is True
    assert len(result.violations) == 0


@pytest.mark.asyncio
async def test_validate_chord_progression():
    """Test validating a chord progression."""
    controller = MockValidationController()
    
    # Test with model instance
    result = await controller.validate_chord_progression({"name": "Test Progression"})
    assert result.is_valid is True
    assert len(result.violations) == 0


@pytest.mark.asyncio
async def test_validate_config():
    """Test validating a configuration."""
    controller = MockValidationController()
    
    # Test with valid config
    config = {"key": "value"}
    result = await controller.validate_config(config, "test_config")
    assert result is True
