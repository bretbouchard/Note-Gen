import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.rhythm_pattern import RhythmPatternData, RhythmPattern
from src.note_gen.models.rhythm_pattern import RhythmNote
import uuid
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
async def mock_db_connection():
    mock_connection = AsyncMock()
    yield mock_connection

@pytest.mark.usefixtures('mock_db_connection')
class TestRhythmPattern:
    async def test_validate_time_signature_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        # Create pattern with valid time signature
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="3/4"
        )
        assert pattern_data.time_signature == "3/4"

    async def test_validate_time_signature_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/0")  # Invalid denominator
        assert "Both numerator and denominator must be positive" in str(exc_info.value)

    async def test_validate_time_signature_invalid_during_instantiation(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/")  # Invalid format
        assert "String should match pattern" in str(exc_info.value)

    async def test_validate_groove_type_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
        pattern_data.groove_type = "swing"
        assert pattern_data.groove_type == "swing"

    async def test_validate_groove_type_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], groove_type="invalid")
        assert "Invalid groove type" in str(exc_info.value)

    async def test_validate_notes_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        valid_notes = [RhythmNote(position=0, duration=1.0)]
        pattern_data = RhythmPatternData(notes=valid_notes)
        assert pattern_data.notes == valid_notes

    async def test_validate_notes_empty(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[])
        assert "List should have at least 1 item" in str(exc_info.value)

    async def test_validate_default_duration_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=2.0)
        assert pattern_data.default_duration == 2.0

    async def test_validate_default_duration_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=0.0)
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_validate_name_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.tags == ["valid_tag"]

    async def test_validate_name_empty(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="",
                data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
                pattern="4 4 4 4",
                complexity=1.0,
                tags=["valid_tag"]
            )
        assert "String should have at least 1 character" in str(exc_info.value)

    async def test_validate_data_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.data == data

    async def test_validate_data_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data="Invalid Data",
                pattern="4 4 4 4",
                complexity=1.0,
                tags=["valid_tag"]
            )
        assert "Input should be a valid dictionary or instance of RhythmPatternData" in str(exc_info.value)

    async def test_validate_pattern_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        pattern.validate_pattern("4 4 4 4")

    async def test_validate_pattern_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
                pattern="invalid_pattern",
                complexity=1.0,
                tags=["valid_tag"]
            ).validate_pattern("invalid_pattern")
        assert "Invalid pattern format" in str(exc_info.value)

    async def test_rhythm_pattern_initialization_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.data.notes[0].position == 0
        assert pattern.data.notes[0].duration == 1.0

    async def test_rhythm_pattern_initialization_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
                pattern="4 4 4 4",
                complexity=1.0,
                tags=None  # Invalid parameter
            )
        assert "Input should be a valid list" in str(exc_info.value)

    async def test_rhythm_pattern_data_validation_notes_empty(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[], duration=1.0)
        assert "List should have at least 1 item" in str(exc_info.value)

    async def test_rhythm_note_validation_velocity_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
        assert "Input should be less than or equal to 127" in str(exc_info.value)

    async def test_rhythm_pattern_data_check_duration_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_rhythm_pattern_creation(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        notes = [
            RhythmNote(
                position=0.0,
                duration=1.0,
                velocity=100,
                is_rest=False,
                accent=None,
                swing_ratio=0.67  # Set to a valid float
            )
        ]
        data = RhythmPatternData(
            notes=notes,
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.2,
            swing_ratio=0.67,
            style="rock",
            default_duration=1.0,
            total_duration=4.0  # Updated to match measure duration
        )
        pattern = RhythmPattern(
            id="test_pattern",
            name="Test Pattern",
            data=data,
            description="A test rhythm pattern",
            tags=["test"],
            complexity=1.0,
            style="rock",
            pattern="4 4 4 4"  # 4 quarter notes = 4 beats, matches 4/4 time signature
        )
        assert pattern.name == "Test Pattern"
        assert pattern.data is not None
        assert len(pattern.tags) == 1
        assert pattern.description == "A test rhythm pattern"
        assert pattern.complexity == 1.0
        assert pattern.style == "rock"
        assert pattern.pattern == [4.0, 4.0, 4.0, 4.0]  # Updated to match the actual stored value

    async def test_rhythm_pattern_data_creation(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        notes = [
            RhythmNote(
                position=0.0,
                duration=1.0,
                velocity=100,
                is_rest=False,
                accent=None,
                swing_ratio=0.67  # Set to a valid float
            )
        ]
        pattern_data = RhythmPatternData(
            notes=notes,
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.0,
            swing_ratio=0.67,
            default_duration=1.0,
            total_duration=4.0,  # Updated to match measure duration
            accent_pattern=[],
            groove_type="straight",
            variation_probability=0.0,
            duration=1.0,
            style="basic"
        )
        assert pattern_data.time_signature == "4/4"
        assert len(pattern_data.notes) == 1
        assert pattern_data.style == "basic"
        assert not pattern_data.swing_enabled

    async def test_note_pattern_creation(self, mock_db_connection):
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern = RhythmPatternData(
            id=str(uuid.uuid4()),
            notes=[RhythmNote(position=0, duration=1)],
            data=[1, 2, 3],
            is_test=True
        )
        assert pattern.notes is not None

    async def test_rhythm_note_validation_velocity_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
        assert "Input should be less than or equal to 127" in str(exc_info.value)

    async def test_rhythm_pattern_data_check_duration_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_validate_default_duration(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        from pydantic import ValidationError
        try:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=-1.0)
            assert False, "Expected ValidationError was not raised for negative default duration"
        except ValidationError as e:
            errors = e.errors()
            assert any("Input should be greater than 0" in str(err["msg"]) for err in errors)

    async def test_validate_time_signature(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        from pydantic import ValidationError
        try:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="invalid")
            assert False, "Expected ValidationError was not raised for invalid time signature"
        except ValidationError as e:
            errors = e.errors()
            assert any("String should match pattern" in str(err["msg"]) for err in errors)

    async def test_validate_swing_ratio(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            swing_ratio=0.5
        )
        assert data.swing_ratio == 0.5
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                swing_ratio=0.25
            )
        assert "Input should be greater than or equal to 0.5" in str(exc_info.value)

    async def test_validate_humanize_amount(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            humanize_amount=0.5
        )
        assert data.humanize_amount == 0.5
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                humanize_amount=1.5
            )
        assert "Input should be less than or equal to 1" in str(exc_info.value)

    async def test_validate_accent_pattern(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        # Test valid accent pattern
        pattern = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            accent_pattern=["0.5", "0.8"]
        )
        assert pattern.accent_pattern == ["0.5", "0.8"]
        
        # Test invalid accent pattern
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                accent_pattern=["-0.5", "2.5"]
            )
        assert "Invalid accent value. Must be a float between 0.0 and 2.0" in str(exc_info.value)

    async def test_validate_groove_type(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            groove_type="swing"
        )
        assert data.groove_type == "swing"
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                groove_type="invalid"
            )
        assert "Invalid groove type. Must be one of: straight, swing, shuffle" in str(exc_info.value)

    async def test_validate_variation_probability(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            variation_probability=0.5
        )
        assert data.variation_probability == 0.5
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                variation_probability=1.5
            )
        assert "Input should be less than or equal to 1" in str(exc_info.value)

    async def test_validate_notes(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        # For a non-empty case, it should pass without error:
        valid_notes = [RhythmNote(position=0, duration=1.0)]
        data = RhythmPatternData(notes=valid_notes)
        assert data.notes == valid_notes
        
        # Test empty notes case
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[])
        assert "List should have at least 1 item" in str(exc_info.value)