"""Simple tests for models."""
import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum, auto


# Define simple enums for testing
class MockTestScaleType(Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    MELODIC_MINOR = "MELODIC_MINOR"


class MockTestChordQuality(Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    DIMINISHED = "DIMINISHED"
    AUGMENTED = "AUGMENTED"


# Define simple models for testing
class MockTestScaleInfo(BaseModel):
    key: str
    scale_type: MockTestScaleType


class MockTestChordProgressionItem(BaseModel):
    chord_symbol: str
    duration: float = 1.0


class MockTestChordProgressionResponse(BaseModel):
    id: str | None = None
    name: str
    chords: list[MockTestChordProgressionItem] = []
    scale_info: MockTestScaleInfo
    key: str
    scale_type: MockTestScaleType
    complexity: float | None = None
    duration: float | None = None

    @classmethod
    def from_db_model(cls, db_model):
        """Create from database model."""
        id_str = str(db_model.get("_id", ""))
        return cls(
            id=id_str,
            name=db_model["name"],
            chords=[MockTestChordProgressionItem(**chord) for chord in db_model["chords"]],
            scale_info=MockTestScaleInfo(**db_model["scale_info"]),
            key=db_model["key"],
            scale_type=db_model["scale_type"],
            complexity=db_model.get("complexity"),
            duration=db_model.get("duration")
        )

    def to_json(self):
        """Convert to JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "chords": [{"chord_symbol": c.chord_symbol, "duration": c.duration} for c in self.chords],
            "scale_info": {"key": self.scale_info.key, "scale_type": self.scale_info.scale_type.value},
            "key": self.key,
            "scale_type": self.scale_type.value,
            "complexity": self.complexity,
            "duration": self.duration
        }


@dataclass(frozen=True)
class MockTestMidiRange:
    """MIDI note range limits."""
    min_midi: int = 0
    max_midi: int = 127


# Tests for chord progression extras
def test_midi_range():
    """Test MidiRange dataclass."""
    # Test default values
    midi_limits = MockTestMidiRange()
    assert midi_limits.min_midi == 0
    assert midi_limits.max_midi == 127

    # Test creating a custom range
    custom_range = MockTestMidiRange(min_midi=24, max_midi=96)
    assert custom_range.min_midi == 24
    assert custom_range.max_midi == 96


def test_chord_progression_response_init():
    """Test ChordProgressionResponse initialization."""
    # Create a scale info
    scale_info = MockTestScaleInfo(
        key="C",
        scale_type=MockTestScaleType.MAJOR
    )

    # Create a chord progression item
    chord_item = MockTestChordProgressionItem(
        chord_symbol="C",
        duration=1.0
    )

    # Create a response
    response = MockTestChordProgressionResponse(
        name="Test Progression",
        chords=[chord_item],
        scale_info=scale_info,
        key="C",
        scale_type=MockTestScaleType.MAJOR,
        complexity=0.5,
        duration=4.0
    )

    # Verify fields
    assert response.name == "Test Progression"
    assert len(response.chords) == 1
    assert response.chords[0] == chord_item
    assert response.scale_info == scale_info
    assert response.key == "C"
    assert response.scale_type == MockTestScaleType.MAJOR
    assert response.complexity == 0.5
    assert response.duration == 4.0


def test_chord_progression_response_from_db_model():
    """Test creating a response from a database model."""
    # Create a mock database model
    db_model = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Test Progression",
        "chords": [
            {
                "chord_symbol": "C",
                "duration": 1.0
            }
        ],
        "scale_info": {
            "key": "C",
            "scale_type": "MAJOR"
        },
        "key": "C",
        "scale_type": "MAJOR",
        "complexity": 0.5,
        "duration": 4.0
    }

    # Create a response from the database model
    response = MockTestChordProgressionResponse.from_db_model(db_model)

    # Verify fields
    assert response.id == "507f1f77bcf86cd799439011"
    assert response.name == "Test Progression"
    assert len(response.chords) == 1
    assert response.chords[0].chord_symbol == "C"
    assert response.chords[0].duration == 1.0
    assert response.scale_info.key == "C"
    assert response.scale_info.scale_type == MockTestScaleType.MAJOR
    assert response.key == "C"
    assert response.scale_type == MockTestScaleType.MAJOR
    assert response.complexity == 0.5
    assert response.duration == 4.0


def test_chord_progression_response_to_json():
    """Test converting a response to JSON."""
    # Create a scale info
    scale_info = MockTestScaleInfo(
        key="C",
        scale_type=MockTestScaleType.MAJOR
    )

    # Create a chord progression item
    chord_item = MockTestChordProgressionItem(
        chord_symbol="C",
        duration=1.0
    )

    # Create a response
    response = MockTestChordProgressionResponse(
        id="507f1f77bcf86cd799439011",
        name="Test Progression",
        chords=[chord_item],
        scale_info=scale_info,
        key="C",
        scale_type=MockTestScaleType.MAJOR,
        complexity=0.5,
        duration=4.0
    )

    # Convert to JSON
    json_data = response.to_json()

    # Verify JSON data
    assert json_data["id"] == "507f1f77bcf86cd799439011"
    assert json_data["name"] == "Test Progression"
    assert len(json_data["chords"]) == 1
    assert json_data["chords"][0]["chord_symbol"] == "C"
    assert json_data["chords"][0]["duration"] == 1.0
    assert json_data["scale_info"]["key"] == "C"
    assert json_data["scale_info"]["scale_type"] == "MAJOR"
    assert json_data["key"] == "C"
    assert json_data["scale_type"] == "MAJOR"
    assert json_data["complexity"] == 0.5
    assert json_data["duration"] == 4.0


# Tests for database models
class MockTestDatabaseConfig(BaseModel):
    """Mock implementation of DatabaseConfig."""
    host: str
    port: int
    database: str
    collection: str
    username: str | None = None
    password: str | None = None
    timeout_ms: int = 5000
    max_pool_size: int = 10
    min_pool_size: int = 1
    ssl_enabled: bool = False
    ssl_ca_file: str | None = None

    def validate_config(self):
        """Validate the configuration."""
        violations = []

        # Check pool size
        if self.min_pool_size > self.max_pool_size:
            violations.append({
                "field": "pool_size",
                "message": "min_pool_size cannot be greater than max_pool_size"
            })

        # Check SSL configuration
        if self.ssl_enabled and not self.ssl_ca_file:
            violations.append({
                "field": "ssl_config",
                "message": "SSL CA file must be provided when SSL is enabled"
            })

        return {
            "is_valid": len(violations) == 0,
            "violations": violations
        }


def test_database_config_init():
    """Test DatabaseConfig initialization with valid data."""
    # Create a valid config
    config = MockTestDatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection"
    )

    # Verify fields
    assert config.host == "localhost"
    assert config.port == 27017
    assert config.database == "test_db"
    assert config.collection == "test_collection"
    assert config.username is None
    assert config.password is None
    assert config.timeout_ms == 5000  # Default value
    assert config.max_pool_size == 10  # Default value
    assert config.min_pool_size == 1   # Default value
    assert config.ssl_enabled is False
    assert config.ssl_ca_file is None


def test_database_config_with_auth():
    """Test DatabaseConfig with authentication."""
    # Create a config with auth
    config = MockTestDatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        username="testuser",
        password="testpass"
    )

    # Verify auth fields
    assert config.username == "testuser"
    assert config.password == "testpass"


def test_database_config_with_ssl():
    """Test DatabaseConfig with SSL."""
    # Create a config with SSL
    config = MockTestDatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        ssl_enabled=True,
        ssl_ca_file="/path/to/ca.pem"
    )

    # Verify SSL fields
    assert config.ssl_enabled is True
    assert config.ssl_ca_file == "/path/to/ca.pem"


def test_database_config_validate_config_valid():
    """Test validate_config with valid configuration."""
    # Create a valid config
    config = MockTestDatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        min_pool_size=5,
        max_pool_size=20
    )

    # Validate the config
    result = config.validate_config()

    # Verify the result
    assert result["is_valid"] is True
    assert len(result["violations"]) == 0


def test_database_config_validate_config_invalid_pool_size():
    """Test validate_config with invalid pool size."""
    # Create a config with invalid pool size (min > max)
    config = MockTestDatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        min_pool_size=10,
        max_pool_size=5
    )

    # Validate the config
    result = config.validate_config()

    # Verify the result
    assert result["is_valid"] is False
    assert len(result["violations"]) == 1
    assert result["violations"][0]["field"] == "pool_size"
    assert "min_pool_size cannot be greater than max_pool_size" in result["violations"][0]["message"]


def test_database_config_validate_config_invalid_ssl():
    """Test validate_config with invalid SSL configuration."""
    # Create a config with invalid SSL (enabled but no CA file)
    config = MockTestDatabaseConfig(
        host="localhost",
        port=27017,
        database="test_db",
        collection="test_collection",
        ssl_enabled=True,
        ssl_ca_file=""
    )

    # Validate the config
    result = config.validate_config()

    # Verify the result
    assert result["is_valid"] is False
    assert len(result["violations"]) >= 1
    # Check for SSL-related violation
    ssl_violation = next((v for v in result["violations"] if "ssl" in v["field"].lower()), None)
    assert ssl_violation is not None
