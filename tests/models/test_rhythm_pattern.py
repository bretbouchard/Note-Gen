import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.patterns import RhythmPatternData, RhythmPattern
from src.note_gen.models.patterns import RhythmNote
import uuid
import logging
from pydantic import ValidationError

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_db_connection():
    return AsyncMock()

class TestRhythmPattern:
    async def test_validate_time_signature_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        # Create pattern with valid time signature
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="3/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=3.0
        )
        assert pattern_data.time_signature == "3/4"

    async def test_validate_time_signature_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="5/0",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=5.0
            )  # Invalid denominator
        assert "Both numerator and denominator must be positive" in str(exc_info.value)

    async def test_validate_time_signature_invalid_during_instantiation(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="5/",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=5.0
            )  # Invalid format
        assert "String should match pattern" in str(exc_info.value)

    async def test_validate_groove_type_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="swing",
            style="jazz",
            duration=4.0
        )
        pattern_data.groove_type = "swing"
        assert pattern_data.groove_type == "swing"

    async def test_validate_groove_type_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="invalid",
                style="jazz",
                duration=4.0
            )
        assert "Invalid groove type" in str(exc_info.value)

    async def test_validate_notes_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        valid_notes = [RhythmNote(position=0, duration=1.0)]
        pattern_data = RhythmPatternData(
            notes=valid_notes,
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        assert pattern_data.notes == valid_notes

    async def test_validate_notes_empty(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
        assert "List should have at least 1 item" in str(exc_info.value)

    async def test_validate_default_duration_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=2.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        assert pattern_data.default_duration == 2.0

    async def test_validate_default_duration_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=0.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_validate_name_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            ),
            pattern="4 4 4 4",
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
                data=RhythmPatternData(
                    notes=[RhythmNote(position=0, duration=1.0)],
                    time_signature="4/4",
                    default_duration=1.0,
                    groove_type="straight",
                    style="jazz",
                    duration=4.0
                ),
                pattern="4 4 4 4",
                complexity=1.0,
                tags=["valid_tag"]
            )
        assert "String should have at least 1 character" in str(exc_info.value)

    async def test_validate_data_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",
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
            data=RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            ),
            pattern="4 4 4 4",
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
                data=RhythmPatternData(
                    notes=[RhythmNote(position=0, duration=1.0)],
                    time_signature="4/4",
                    default_duration=1.0,
                    groove_type="straight",
                    style="jazz",
                    duration=4.0
                ),
                pattern="invalid_pattern",
                complexity=1.0,
                tags=["valid_tag"]
            ).validate_pattern("invalid_pattern")
        assert "Invalid pattern format" in str(exc_info.value)

    async def test_rhythm_pattern_initialization_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.data is not None
        assert len(pattern.tags) == 1
        assert pattern.complexity == 1.0

    async def test_rhythm_pattern_initialization_invalid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data=RhythmPatternData(
                    notes=[RhythmNote(position=0, duration=1.0)],
                    time_signature="4/4",
                    default_duration=1.0,
                    groove_type="straight",
                    style="jazz",
                    duration=4.0
                ),
                pattern="4 4 4 4",
                complexity=1.0,
                tags=None  # Invalid parameter
            )
        assert "Input should be a valid list" in str(exc_info.value)

    async def test_rhythm_pattern_data_validation_notes_empty(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
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
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=-1.0
            )  # Invalid duration
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
        assert pattern.pattern == "4 4 4 4"  # Updated to match the actual stored value

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
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=-1.0
            )  # Invalid duration
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_validate_default_duration(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        try:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=-1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
            assert False, "Expected ValidationError was not raised for negative default duration"
        except ValidationError as e:
            errors = e.errors()
            assert any("Input should be greater than 0" in str(err["msg"]) for err in errors)

    async def test_validate_time_signature(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        try:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="invalid",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
            assert False, "Expected ValidationError was not raised for invalid time signature"
        except ValidationError as e:
            errors = e.errors()
            assert any("String should match pattern" in str(err["msg"]) for err in errors)

    async def test_validate_swing_ratio(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            swing_ratio=0.5
        )
        assert data.swing_ratio == 0.5
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0,
                swing_ratio=0.25
            )
        assert "Input should be greater than or equal to 0.5" in str(exc_info.value)

    async def test_validate_humanize_amount(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            humanize_amount=0.5
        )
        assert data.humanize_amount == 0.5
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0,
                humanize_amount=1.5
            )
        assert "Input should be less than or equal to 1" in str(exc_info.value)

    async def test_validate_accent_pattern(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        # Test valid accent pattern
        pattern = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            accent_pattern=["0.5", "0.8"]
        )
        assert pattern.accent_pattern == ["0.5", "0.8"]
        
        # Test invalid accent pattern
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0,
                accent_pattern=["-0.5", "2.5"]
            )
        assert "Invalid accent value. Must be a float between 0.0 and 2.0" in str(exc_info.value)

    async def test_validate_groove_type(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="swing",
            style="jazz",
            duration=4.0
        )
        assert data.groove_type == "swing"
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="invalid",
                style="jazz",
                duration=4.0
            )
        assert "Invalid groove type. Must be one of: straight, swing, shuffle" in str(exc_info.value)

    async def test_validate_variation_probability(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            variation_probability=0.5
        )
        assert data.variation_probability == 0.5
        
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0,
                variation_probability=1.5
            )
        assert "Input should be less than or equal to 1" in str(exc_info.value)

    async def test_validate_notes(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        # For a non-empty case, it should pass without error:
        valid_notes = [RhythmNote(position=0, duration=1.0)]
        data = RhythmPatternData(
            notes=valid_notes,
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        assert data.notes == valid_notes
        
        # Test empty notes case
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
        assert "List should have at least 1 item" in str(exc_info.value)

    async def test_validate_pattern_required(self, mock_db_connection) -> None:
        """Test that pattern field is required for RhythmPattern."""
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        
        # Create a RhythmNote and RhythmPatternData
        rhythm_note = RhythmNote(position=0, duration=1.0)
        rhythm_data = RhythmPatternData(
            notes=[rhythm_note],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        
        # Attempt to create RhythmPattern without pattern field
        with pytest.raises(ValidationError) as exc_info:
            RhythmPattern(
                name="Test Pattern",
                data=rhythm_data,
                description="Test description",
                tags=["test"]
            )
        
        errors = exc_info.value.errors()
        assert any(error['msg'] == 'Field required' for error in errors)
        logger.debug(f"Error message for missing pattern: {str(exc_info.value)}")
        
        # Now create with valid pattern field
        pattern = RhythmPattern(
            name="Test Pattern",
            data=rhythm_data,
            pattern="1.0 1.0 1.0 1.0",
            description="Test description",
            tags=["test"]
        )
        
        # Verify the pattern was parsed and converted correctly
        assert isinstance(pattern.pattern, list)
        assert len(pattern.pattern) == 4
        assert all(isinstance(dur, float) for dur in pattern.pattern)
        assert pattern.pattern == [1.0, 1.0, 1.0, 1.0]
        
        # Test with invalid pattern string
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                name="Test Pattern",
                data=rhythm_data,
                pattern="1.0 bad 1.0 1.0",
                description="Test description",
                tags=["test"]
            )
        
        assert "Invalid pattern format" in str(exc_info.value)

    async def test_rhythm_pattern_with_rests(self, mock_db_connection) -> None:
        """Test that rhythm patterns properly handle negative values as rests."""
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        
        # Create a rhythm pattern with both notes and rests
        pattern = RhythmPattern(
            name="Test Pattern With Rests",
            pattern=[1.0, -0.5, 2.0],  # 1 beat note, 0.5 beat rest, 2 beat note
            data=RhythmPatternData(
                notes=[
                    # First note (1.0 beat)
                    RhythmNote(position=0, duration=1.0, is_rest=False, velocity=100),
                    # Rest (0.5 beat)
                    RhythmNote(position=1.0, duration=0.5, is_rest=True, velocity=0),
                    # Second note (2.0 beat)
                    RhythmNote(position=1.5, duration=2.0, is_rest=False, velocity=100)
                ],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
        )
        
        # Verify pattern values match expectations
        assert len(pattern.pattern) == 3
        assert pattern.pattern[0] == 1.0
        assert pattern.pattern[1] == -0.5  # Negative value for rest
        assert pattern.pattern[2] == 2.0
        
        # Verify notes in the data match the pattern
        assert len(pattern.data.notes) == 3
        assert pattern.data.notes[0].duration == 1.0
        assert pattern.data.notes[0].is_rest == False
        
        assert pattern.data.notes[1].duration == 0.5
        assert pattern.data.notes[1].is_rest == True  # Verify this is a rest
        
        assert pattern.data.notes[2].duration == 2.0
        assert pattern.data.notes[2].is_rest == False
        
        # Verify total duration
        total_duration = sum(abs(d) for d in pattern.pattern)
        assert total_duration == 3.5  # 1.0 + 0.5 + 2.0 = 3.5

    async def test_rhythm_pattern_creation(self, mock_db_connection) -> None:
        pattern = "4 4 4 4"
        rhythm_pattern = RhythmPattern(name="Test Pattern", pattern=pattern)
        assert rhythm_pattern.pattern == pattern

    async def test_rhythm_pattern_with_rests(self, mock_db_connection) -> None:
        pattern = "1 -1 1 -1"
        rhythm_pattern = RhythmPattern(name="Test Pattern", pattern=pattern)
        assert rhythm_pattern.pattern == pattern

    async def test_validate_pattern_required(self, mock_db_connection) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RhythmPattern(name="Test Pattern")
        errors = exc_info.value.errors()
        assert any(error['msg'] == 'Field required' for error in errors)

    async def test_validate_pattern_format(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        valid_patterns = [
            "4 4 4 4",
            "8 8 8 8 8 8 8 8",
            "2 2 2 2 2 2",
            "16 16 16 16 16 16 16 16 16 16 16 16 16 16 16 16"
        ]
        for pattern in valid_patterns:
            assert RhythmPattern.validate_pattern(pattern) == pattern

    async def test_validate_pattern_invalid_characters(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        invalid_patterns = [
            "4 4 4 a",
            "4.5 4 4 4",
            "4/4 4 4 4",
            "4,4,4,4"
        ]
        for pattern in invalid_patterns:
            with pytest.raises(ValueError) as exc_info:
                RhythmPattern.validate_pattern(pattern)
            assert str(exc_info.value) == 'Pattern must contain only numbers separated by spaces'

    async def test_validate_pattern_empty(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern.validate_pattern("")
        assert str(exc_info.value) == 'Pattern cannot be empty'

    async def test_validate_pattern_type_safety(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        invalid_patterns = [
            12345,
            [4, 4, 4, 4],
            {"pattern": "4 4 4 4"},
            None
        ]
        for pattern in invalid_patterns:
            with pytest.raises(ValueError) as exc_info:
                RhythmPattern.validate_pattern(pattern)
            assert str(exc_info.value) == 'Pattern must be a string'

    async def test_rhythm_pattern_creation(self, mock_db_connection) -> None:
        pattern = "4 4 4 4"
        rhythm_pattern = RhythmPattern(pattern=pattern)
        assert rhythm_pattern.pattern == pattern

    async def test_validate_default_duration_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=2.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        assert pattern_data.default_duration == 2.0

    async def test_validate_name_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            ),
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.tags == ["valid_tag"]

    async def test_validate_data_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.data == data

    async def test_rhythm_pattern_initialization_valid(self, mock_db_connection) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0
        )
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.data is not None
        assert len(pattern.tags) == 1
        assert pattern.complexity == 1.0