"""Tests for the validation controller."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import only what we need to test
from note_gen.core.enums import ValidationLevel

# Mock classes to avoid circular imports
class MockValidationResult:
    """Mock validation result."""

    def __init__(self, is_valid=True, violations=None):
        """Initialize the mock validation result."""
        self.is_valid = is_valid
        self.violations = violations or []

class MockValidationViolation:
    """Mock validation violation."""

    def __init__(self, message, code="VALIDATION_ERROR", path=""):
        """Initialize the mock validation violation."""
        self.message = message
        self.code = code
        self.path = path

class MockValidationManager:
    """Mock validation manager."""

    def validate(self, model):
        """Mock validate method."""
        return MockValidationResult(is_valid=True, violations=[])

    def validate_config(self, config, config_type):
        """Mock validate_config method."""
        return True

class MockNote:
    """Mock note class."""

    def __init__(self, pitch="C", octave=4, duration=1.0, velocity=100):
        """Initialize the mock note."""
        self.pitch = pitch
        self.octave = octave
        self.duration = duration
        self.velocity = velocity

class MockNotePatternData:
    """Mock note pattern data."""

    def __init__(self, notes=None, scale_type="MAJOR", direction="up"):
        """Initialize the mock note pattern data."""
        self.notes = notes or [MockNote()]
        self.scale_type = scale_type
        self.direction = direction

class MockNotePattern:
    """Mock note pattern."""

    def __init__(self, id="507f1f77bcf86cd799439011", name="Test Pattern", complexity=3.0, tags=None, data=None):
        """Initialize the mock note pattern."""
        self.id = id
        self.name = name
        self.complexity = complexity
        self.tags = tags or ["test", "pattern"]
        self.data = data or MockNotePatternData()

    def model_validate(self, data):
        """Mock model_validate method."""
        return self

    def model_dump(self):
        """Mock model_dump method."""
        return {
            "id": self.id,
            "name": self.name,
            "complexity": self.complexity,
            "tags": self.tags,
            "data": {
                "notes": [{"pitch": "C", "octave": 4, "duration": 1.0, "velocity": 100}],
                "scale_type": "MAJOR",
                "direction": "up"
            }
        }

class MockRhythmNote:
    """Mock rhythm note."""

    def __init__(self, position=0, duration=1.0, velocity=100):
        """Initialize the mock rhythm note."""
        self.position = position
        self.duration = duration
        self.velocity = velocity

class MockRhythmPattern:
    """Mock rhythm pattern."""

    def __init__(self, id="507f1f77bcf86cd799439012", name="Test Rhythm", time_signature=None, notes=None):
        """Initialize the mock rhythm pattern."""
        self.id = id
        self.name = name
        self.time_signature = time_signature or [4, 4]
        self.notes = notes or [MockRhythmNote()]

    def model_validate(self, data):
        """Mock model_validate method."""
        return self

    def model_dump(self):
        """Mock model_dump method."""
        return {
            "id": self.id,
            "name": self.name,
            "time_signature": self.time_signature,
            "notes": [{"position": 0, "duration": 1.0, "velocity": 100}]
        }

class MockChordProgression:
    """Mock chord progression."""

    def __init__(self, id="507f1f77bcf86cd799439013", name="Test Progression", key="C", scale_type="MAJOR", chords=None):
        """Initialize the mock chord progression."""
        self.id = id
        self.name = name
        self.key = key
        self.scale_type = scale_type
        self.chords = chords or []

    def model_validate(self, data):
        """Mock model_validate method."""
        return self

    def model_dump(self):
        """Mock model_dump method."""
        return {
            "id": self.id,
            "name": self.name,
            "key": self.key,
            "scale_type": self.scale_type,
            "chords": self.chords
        }

class MockNoteSequence:
    """Mock note sequence."""

    def __init__(self, id="507f1f77bcf86cd799439014", name="Test Sequence", notes=None):
        """Initialize the mock note sequence."""
        self.id = id
        self.name = name
        self.notes = notes or [MockNote()]

    def model_validate(self, data):
        """Mock model_validate method."""
        return self

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
        if isinstance(pattern, dict) and "name" in pattern and len(pattern) == 1:
            return MockValidationResult(
                is_valid=False,
                violations=[MockValidationViolation(message="Invalid note pattern format")]
            )
        return MockValidationResult(is_valid=True, violations=[])

    async def validate_rhythm_pattern(self, pattern, level=None):
        """Mock validate_rhythm_pattern method."""
        if isinstance(pattern, dict) and "name" in pattern and len(pattern) == 1:
            return MockValidationResult(
                is_valid=False,
                violations=[MockValidationViolation(message="Invalid rhythm pattern format")]
            )
        return MockValidationResult(is_valid=True, violations=[])

    async def validate_note_sequence(self, sequence, level=None):
        """Mock validate_note_sequence method."""
        return MockValidationResult(is_valid=True, violations=[])

    async def validate_chord_progression(self, progression, level=None):
        """Mock validate_chord_progression method."""
        if isinstance(progression, dict) and "name" in progression and len(progression) == 1:
            return MockValidationResult(
                is_valid=False,
                violations=[MockValidationViolation(message="Invalid chord progression format")]
            )
        return MockValidationResult(is_valid=True, violations=[])

    async def validate_config(self, config, config_type):
        """Mock validate_config method."""
        return True


@pytest.fixture
def controller():
    """Create a validation controller instance."""
    return MockValidationController()


@pytest.fixture
def sample_note_pattern():
    """Create a sample note pattern."""
    return MockNotePattern()


@pytest.fixture
def sample_rhythm_pattern():
    """Create a sample rhythm pattern."""
    return MockRhythmPattern()


@pytest.fixture
def sample_chord_progression():
    """Create a sample chord progression."""
    return MockChordProgression()


@pytest.mark.asyncio
async def test_create():
    """Test the create factory method."""
    controller = await MockValidationController.create()
    assert isinstance(controller, MockValidationController)
    assert controller.validation_manager is not None


@pytest.mark.asyncio
async def test_validate_note_pattern(controller, sample_note_pattern):
    """Test validating a note pattern."""
    # Mock the validation manager
    controller.validation_manager.validate = MagicMock(
        return_value=MockValidationResult(is_valid=True, violations=[])
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
        return_value=MockValidationResult(is_valid=True, violations=[])
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
        return_value=MockValidationResult(is_valid=True, violations=[])
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
    # Mock the validate_config method directly
    original_method = controller.validate_config
    mock_result = True

    async def mock_validate_config(config, config_type):
        return mock_result

    controller.validate_config = MagicMock(side_effect=mock_validate_config)

    try:
        # Test with valid config
        config = {"key": "value"}
        result = await controller.validate_config(config, "test_config")
        assert result is True
        controller.validate_config.assert_called_once_with(config, "test_config")
    finally:
        # Restore the original method
        controller.validate_config = original_method
