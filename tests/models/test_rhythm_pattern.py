import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.patterns import RhythmPatternData, RhythmPattern
from src.note_gen.models.patterns import RhythmNote , ChordPatternItem
import uuid
import logging
from pydantic import ValidationError

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_db_connection() -> AsyncMock:
    return AsyncMock()

class TestRhythmPattern:
    async def test_validate_time_signature_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_time_signature_invalid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="5/0",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=3.0
            )
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_validate_time_signature_invalid_during_instantiation(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="5/",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=3.0
            )
        assert "String should match pattern" in str(exc_info.value)

    async def test_validate_groove_type_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_groove_type(self, mock_db_connection: AsyncMock) -> None:
        # Test valid groove types
        for valid_groove in ['straight', 'swing', 'shuffle']:
            data = RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature='4/4',
                default_duration=1.0,
                groove_type=valid_groove,
                style='jazz',
                duration=4.0
            )
            assert data.groove_type == valid_groove
    
        # Test invalid groove type
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature='4/4',
                default_duration=1.0,
                groove_type='invalid',
                style='jazz',
                duration=4.0
            )
        
        # Check for Pydantic v2's error format
        error_message = str(exc_info.value)
        assert "Invalid groove type. Must be one of: straight, swing, shuffle" in error_message
    
    async def test_validate_notes_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_notes_empty(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_default_duration_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_default_duration_invalid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_name_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_name_empty(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
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

    async def test_validate_data_valid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        
        # Create RhythmPatternData model directly instead of using a dictionary
        rhythm_data = RhythmPatternData(
            name="Default Pattern",
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            swing_ratio=0.67,
            humanize_amount=0.5,
            accent_pattern=[0.5, 0.8],  # Use float values instead of strings
            variation_probability=0.5
        )
        
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=rhythm_data,
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        
        # Verify the data was properly set
        assert pattern.data.time_signature == "4/4"
        assert pattern.data.default_duration == 1.0
        assert pattern.data.groove_type == "straight"
        assert pattern.data.style == "jazz"
        assert pattern.data.duration == 4.0
        assert pattern.data.swing_ratio == 0.67
        assert pattern.data.humanize_amount == 0.5
        assert pattern.data.accent_pattern == [0.5, 0.8]
        assert pattern.data.variation_probability == 0.5

    async def test_validate_data_invalid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data="Invalid Data",
                pattern="4 4 4 4",
                complexity=1.0,
                tags=["valid_tag"]
            )
        assert "Input should be a valid dictionary or instance of RhythmPatternData" in str(exc_info.value)

    async def test_validate_pattern_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_pattern_invalid(self, mock_db_connection: AsyncMock) -> None:
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
            )
        assert "Pattern must contain only numbers separated by spaces" in str(exc_info.value)

    async def test_rhythm_pattern_initialization_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_rhythm_pattern_initialization_invalid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_rhythm_pattern_data_validation_notes_empty(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_rhythm_note_validation_velocity_invalid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
        assert "Input should be less than or equal to 127" in str(exc_info.value)

    async def test_rhythm_pattern_data_check_duration_invalid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_rhythm_pattern_creation(self, mock_db_connection: AsyncMock) -> None:
        pattern = RhythmPattern(
            pattern="1 1 1 1",
            name="Test Pattern",
            description="Test description",
            complexity=1.0,
            data=RhythmPatternData(
                name="Test Data",
                notes=[
                    RhythmNote(position=0, duration=1.0, is_rest=False, velocity=100),
                    RhythmNote(position=1.0, duration=1.0, is_rest=False, velocity=100),
                    RhythmNote(position=2.0, duration=1.0, is_rest=False, velocity=100),
                    RhythmNote(position=3.0, duration=1.0, is_rest=False, velocity=100)
                ],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                pattern="4 4 4 4"
            )
        )
        assert pattern.pattern == "1 1 1 1"

    async def test_rhythm_pattern_with_rests(self, mock_db_connection: AsyncMock) -> None:
        """Test that rhythm patterns properly handle negative values as rests."""
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        
        # Create a rhythm pattern with both notes and rests
        pattern = RhythmPattern(
            name="Test Pattern With Rests",
            pattern="1 -1 2",  # 1 beat note, 1 beat rest, 2 beat note
            data=RhythmPatternData(
                notes=[
                    # First note (1.0 beat)
                    RhythmNote(position=0, duration=1.0, is_rest=False, velocity=100),
                    # Rest (1.0 beat)
                    RhythmNote(position=1.0, duration=1.0, is_rest=True, velocity=0),
                    # Second note (2.0 beat)
                    RhythmNote(position=2.0, duration=2.0, is_rest=False, velocity=100)
                ],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
        )
        
        # Verify pattern string is as expected
        assert pattern.pattern == "1 -1 2"
        
        # Parse the pattern string to verify values
        pattern_values = [float(x) for x in pattern.pattern.split()]
        assert len(pattern_values) == 3
        assert pattern_values[0] == 1.0
        assert pattern_values[1] == -1.0  # Negative value for rest
        assert pattern_values[2] == 2.0
        
        # Verify notes in the data match the pattern
        assert len(pattern.data.notes) == 3
        assert pattern.data.notes[0].duration == 1.0
        assert pattern.data.notes[0].is_rest == False
        
        assert pattern.data.notes[1].duration == 1.0
        assert pattern.data.notes[1].is_rest == True  # Verify this is a rest
        
        assert pattern.data.notes[2].duration == 2.0
        assert pattern.data.notes[2].is_rest == False
        
        # Verify total duration
        total_duration = sum(abs(d) for d in pattern_values)
        assert total_duration == 4.0  # 1.0 + 1.0 + 2.0 = 4.0

    async def test_rhythm_pattern_with_rests_basic(self, mock_db_connection: AsyncMock) -> None:
        pattern = "1 -1 1 -1"
        # Create a RhythmPatternData instance for the required data field
        rhythm_note = RhythmNote(position=0, duration=1.0)
        rhythm_data = RhythmPatternData(
            notes=[rhythm_note],
            time_signature="4/4",
            default_duration=1.0,
        )
        rhythm_pattern = RhythmPattern(name="Test Pattern", pattern=pattern, data=rhythm_data)
        assert rhythm_pattern.pattern == pattern

    async def test_validate_pattern_required(self, mock_db_connection: AsyncMock) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RhythmPattern(name="Test Pattern")
        errors = exc_info.value.errors()
        print("Validation errors:", errors)
        print("Error types:", [error.get('type') for error in errors])
        # Update the assertion to match Pydantic v2 error types
        assert any('value_error' in error.get('type', '') for error in errors)

    async def test_validate_pattern_format(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        valid_patterns = [
            [4, 4, 4, 4],
            [8, 8, 8, 8, 8, 8, 8, 8],
            [2, 2, 2, 2, 2, 2],
            [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16]
        ]
        for pattern in valid_patterns:
            assert RhythmPattern.validate_pattern(pattern) == pattern

    async def test_validate_pattern_invalid_characters(self, mock_db_connection: AsyncMock) -> None:
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
                RhythmPattern(
                    id="1",
                    name="Test Pattern",
                    data=RhythmPatternData(
                        notes=[RhythmNote(position=0, duration=1.0)],
                        time_signature="4/4",
                        default_duration=1.0
                    ),
                    pattern=pattern
                )
            assert "Pattern must contain only numbers separated by spaces" in str(exc_info.value)

    async def test_validate_pattern_empty(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern.validate_pattern("")
        assert str(exc_info.value) == 'Pattern cannot be empty'

    async def test_validate_pattern_type_safety(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        invalid_patterns = [
            12345,
            [4, 4, 4, 4],
            None
        ]
        for pattern in invalid_patterns:
            with pytest.raises(ValueError) as exc_info:
                RhythmPattern.validate_pattern(pattern)
            if pattern is None:
                assert str(exc_info.value) == 'Pattern cannot be None'
            else:
                assert str(exc_info.value) == 'Pattern must be a string'

    async def test_rhythm_pattern_creation(self, mock_db_connection: AsyncMock) -> None:
        pattern = "4 4 4 4"
        rhythm_pattern = RhythmPattern(pattern=pattern, name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="4/4", default_duration=1.0))
        assert rhythm_pattern.pattern == pattern

    async def test_validate_default_duration_valid_v2(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_rhythm_pattern_with_rests_basic_v2(self, mock_db_connection: AsyncMock) -> None:
        pattern = "1 -1 1 -1"
        # Create a RhythmPatternData instance for the required data field
        rhythm_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
        )
        rhythm_pattern = RhythmPattern(name="Test Pattern", pattern=pattern, data=rhythm_data)
        assert rhythm_pattern.pattern == pattern

    async def test_validate_pattern_required_v2(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
        assert "Field required" in str(exc_info.value)

    async def test_validate_name_valid(self, mock_db_connection: AsyncMock) -> None:
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
                duration=4.0,
                swing_ratio=0.67,
                humanize_amount=0.5,
                accent_pattern=["0.5", "0.8"],
                variation_probability=0.5
            ),
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.tags == ["valid_tag"]

    async def test_validate_data_valid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        
        # Create RhythmPatternData model directly instead of using a dictionary
        rhythm_data = RhythmPatternData(
            name="Default Pattern",
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            swing_ratio=0.67,
            humanize_amount=0.5,
            accent_pattern=[0.5, 0.8],  # Use float values instead of strings
            variation_probability=0.5
        )
        
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=rhythm_data,
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        
        # Verify the data was properly set
        assert pattern.data.time_signature == "4/4"
        assert pattern.data.default_duration == 1.0
        assert pattern.data.groove_type == "straight"
        assert pattern.data.style == "jazz"
        assert pattern.data.duration == 4.0
        assert pattern.data.swing_ratio == 0.67
        assert pattern.data.humanize_amount == 0.5
        assert pattern.data.accent_pattern == [0.5, 0.8]
        assert pattern.data.variation_probability == 0.5

    async def test_rhythm_pattern_initialization_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_rhythm_pattern_initialization_invalid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_groove_type_invalid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature='4/4',
                default_duration=1.0,
                groove_type='invalid',
                style='jazz',
                duration=4.0
            )
        assert "Invalid groove type. Must be one of: straight, swing, shuffle" in str(exc_info.value)

    async def test_validate_variation_probability(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_notes(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_pattern_required(self, mock_db_connection: AsyncMock) -> None:
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
        print("Validation errors:", errors)
        print("Error types:", [error.get('type') for error in errors])
        print("Error messages:", [error.get('msg') for error in errors])
        
        # Check for the specific error type and message
        assert any("value_error" == error.get('type', '') for error in errors)
        assert any("Pattern must be provided" in error.get('msg', '') for error in errors)
        
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

    async def test_rhythm_pattern_with_rests(self, mock_db_connection: AsyncMock) -> None:
        """Test that rhythm patterns properly handle negative values as rests."""
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        
        # Create a rhythm pattern with both notes and rests
        pattern = RhythmPattern(
            name="Test Pattern With Rests",
            pattern="1 -1 2",  # 1 beat note, 1 beat rest, 2 beat note
            data=RhythmPatternData(
                notes=[
                    # First note (1.0 beat)
                    RhythmNote(position=0, duration=1.0, is_rest=False, velocity=100),
                    # Rest (1.0 beat)
                    RhythmNote(position=1.0, duration=1.0, is_rest=True, velocity=0),
                    # Second note (2.0 beat)
                    RhythmNote(position=2.0, duration=2.0, is_rest=False, velocity=100)
                ],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            )
        )
        
        # Verify pattern string is as expected
        assert pattern.pattern == "1 -1 2"
        
        # Parse the pattern string to verify values
        pattern_values = [float(x) for x in pattern.pattern.split()]
        assert len(pattern_values) == 3
        assert pattern_values[0] == 1.0
        assert pattern_values[1] == -1.0  # Negative value for rest
        assert pattern_values[2] == 2.0
        
        # Verify notes in the data match the pattern
        assert len(pattern.data.notes) == 3
        assert pattern.data.notes[0].duration == 1.0
        assert pattern.data.notes[0].is_rest == False
        
        assert pattern.data.notes[1].duration == 1.0
        assert pattern.data.notes[1].is_rest == True  # Verify this is a rest
        
        assert pattern.data.notes[2].duration == 2.0
        assert pattern.data.notes[2].is_rest == False
        
        # Verify total duration
        total_duration = sum(abs(d) for d in pattern_values)
        assert total_duration == 4.0  # 1.0 + 1.0 + 2.0 = 4.0

    async def test_rhythm_pattern_creation(self, mock_db_connection: AsyncMock) -> None:
        pattern = "4 4 4 4"
        # Create a RhythmPatternData instance for the required data field
        rhythm_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0
        )
        rhythm_pattern = RhythmPattern(pattern=pattern, name="Test Pattern", data=rhythm_data)
        assert rhythm_pattern.pattern == pattern

    async def test_rhythm_pattern_with_rests_basic(self, mock_db_connection: AsyncMock) -> None:
        pattern = "1 -1 1 -1"
        # Create a RhythmPatternData instance for the required data field
        rhythm_note = RhythmNote(position=0, duration=1.0)
        rhythm_data = RhythmPatternData(
            notes=[rhythm_note],
            time_signature="4/4",
            default_duration=1.0,
        )
        rhythm_pattern = RhythmPattern(name="Test Pattern", pattern=pattern, data=rhythm_data)
        assert rhythm_pattern.pattern == pattern

    async def test_validate_pattern_required(self, mock_db_connection: AsyncMock) -> None:
        with pytest.raises(ValidationError) as exc_info:
            RhythmPattern(name="Test Pattern")
        errors = exc_info.value.errors()
        print("Validation errors:", errors)
        print("Error types:", [error.get('type') for error in errors])
        # Update the assertion to match Pydantic v2 error types
        assert any('value_error' in error.get('type', '') for error in errors)

    async def test_validate_pattern_format(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        valid_patterns = [
            [4, 4, 4, 4],
            [8, 8, 8, 8, 8, 8, 8, 8],
            [2, 2, 2, 2, 2, 2],
            [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16]
        ]
        for pattern in valid_patterns:
            assert RhythmPattern.validate_pattern(pattern) == pattern

    async def test_validate_pattern_invalid_characters(self, mock_db_connection: AsyncMock) -> None:
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
                RhythmPattern(
                    id="1",
                    name="Test Pattern",
                    data=RhythmPatternData(
                        notes=[RhythmNote(position=0, duration=1.0)],
                        time_signature="4/4",
                        default_duration=1.0
                    ),
                    pattern=pattern
                )
            assert "Pattern must contain only numbers separated by spaces" in str(exc_info.value)

    async def test_validate_pattern_empty(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern.validate_pattern("")
        assert str(exc_info.value) == 'Pattern cannot be empty'

    async def test_validate_pattern_type_safety(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        invalid_patterns = [
            12345,
            [4, 4, 4, 4],
            None
        ]
        for pattern in invalid_patterns:
            with pytest.raises(ValueError) as exc_info:
                RhythmPattern.validate_pattern(pattern)
            if pattern is None:
                assert str(exc_info.value) == 'Pattern cannot be None'
            else:
                assert str(exc_info.value) == 'Pattern must be a string'

    async def test_rhythm_pattern_creation(self, mock_db_connection: AsyncMock) -> None:
        pattern = "4 4 4 4"
        rhythm_pattern = RhythmPattern(pattern=pattern, name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="4/4", default_duration=1.0))
        assert rhythm_pattern.pattern == pattern

    async def test_validate_default_duration_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_name_valid(self, mock_db_connection: AsyncMock) -> None:
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
                duration=4.0,
                swing_ratio=0.67,
                humanize_amount=0.5,
                accent_pattern=["0.5", "0.8"],
                variation_probability=0.5
            ),
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.tags == ["valid_tag"]

    async def test_validate_data_valid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        
        # Create RhythmPatternData model directly instead of using a dictionary
        rhythm_data = RhythmPatternData(
            name="Default Pattern",
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            swing_ratio=0.67,
            humanize_amount=0.5,
            accent_pattern=[0.5, 0.8],  # Use float values instead of strings
            variation_probability=0.5
        )
        
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=rhythm_data,
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
        
        # Verify the data was properly set
        assert pattern.data.time_signature == "4/4"
        assert pattern.data.default_duration == 1.0
        assert pattern.data.groove_type == "straight"
        assert pattern.data.style == "jazz"
        assert pattern.data.duration == 4.0
        assert pattern.data.swing_ratio == 0.67
        assert pattern.data.humanize_amount == 0.5
        assert pattern.data.accent_pattern == [0.5, 0.8]
        assert pattern.data.variation_probability == 0.5

    async def test_rhythm_pattern_initialization_valid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_rhythm_pattern_initialization_invalid(self, mock_db_connection: AsyncMock) -> None:
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

    async def test_validate_groove_type_invalid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature='4/4',
                default_duration=1.0,
                groove_type='invalid',
                style='jazz',
                duration=4.0
            )
        assert "Invalid groove type. Must be one of: straight, swing, shuffle" in str(exc_info.value)

    async def test_validate_pattern_valid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        # Create pattern with valid pattern
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            pattern="4 4 4 4"
        )
        assert pattern_data.pattern == "4 4 4 4"

    async def test_validate_pattern_invalid(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0,
                pattern="invalid_pattern"
            )
        assert "Pattern must contain only numbers separated by spaces" in str(exc_info.value)

    async def test_validate_duration_positive(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            pattern="4 4 4 4"
        )
        assert pattern_data.duration == 4.0

    async def test_validate_duration_negative(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=-4.0,
                pattern="4 4 4 4"
            )
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_validate_duration_match_pattern(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            pattern="4 4 4 4"
        )
        assert pattern_data.duration == 4.0

    async def test_validate_duration_mismatch_pattern(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=3.0,
                pattern="4 4 4 4"
            )
        assert "Duration does not match pattern duration" in str(exc_info.value)

    async def test_validate_duration_positive(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            pattern="4 4 4 4"
        )
        assert pattern_data.duration == 4.0

    async def test_validate_duration_negative(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=-4.0,
                pattern="4 4 4 4"
            )
        assert "Input should be greater than 0" in str(exc_info.value)

    async def test_validate_default_duration_valid_v3(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            groove_type="straight",
            style="jazz",
            duration=4.0,
            pattern="4 4 4 4"
        )
        assert pattern_data.default_duration == 1.0

    async def test_rhythm_pattern_with_rests_basic_v3(self, mock_db_connection: AsyncMock) -> None:
        pattern = "1 -1 1 -1"
        # Create a RhythmPatternData instance for the required data field
        rhythm_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="4/4",
            default_duration=1.0,
            pattern="1 -1 1 -1"
        )
        rhythm_pattern = RhythmPattern(
            name="Test Pattern",
            pattern=pattern,
            data=rhythm_data,
            description="Test description",
            complexity=1.0
        )
        assert rhythm_pattern.pattern == pattern

    async def test_validate_pattern_required_v3(self, mock_db_connection: AsyncMock) -> None:
        # Setup mock return value
        mock_db_connection.return_value.__aenter__.return_value = AsyncMock()
        with pytest.raises(ValidationError) as exc_info:
            RhythmPatternData(
                notes=[RhythmNote(position=0, duration=1.0)],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0,
                pattern="4 4 4 4"
            )
        assert "Field required" in str(exc_info.value)

    async def test_chord_pattern_item_initialization(self, mock_db_connection: AsyncMock) -> None:
        # Test valid initialization
        item = ChordPatternItem(degree=1, quality="MAJOR", duration=4.0)
        assert item.degree == 1
        assert item.quality == "MAJOR"
        assert item.duration == 4.0
        
        # Test Roman numeral as degree
        item = ChordPatternItem(degree="I", quality="MAJOR", duration=4.0)
        assert item.degree == 1
        assert item.quality == "MAJOR"
        
        # Test initialization with default duration
        item = ChordPatternItem(degree=1, quality="MAJOR")
        assert item.duration == 4.0  # Default value
        
        # Test initialization with inversion
        item = ChordPatternItem(degree=1, quality="MAJOR", inversion=1)
        assert item.inversion == 1

    async def test_chord_pattern_item_validation(self, mock_db_connection: AsyncMock) -> None:
        # Test invalid degree
        with pytest.raises(ValidationError):
            ChordPatternItem(degree=8, quality="MAJOR")  # Degree outside valid range
        
        # Test invalid degree type
        with pytest.raises(ValidationError):
            ChordPatternItem(degree="not_a_degree", quality="MAJOR")
        
        # Test negative duration
        with pytest.raises(ValidationError):
            ChordPatternItem(degree=1, quality="MAJOR", duration=-1.0)

    async def test_chord_progression_pattern_initialization(self, mock_db_connection: AsyncMock) -> None:
        # Test valid initialization with pattern items
        pattern_items = [
            ChordPatternItem(degree=1, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=4, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=5, quality="MAJOR", duration=4.0),
            ChordPatternItem(degree=1, quality="MAJOR", duration=4.0)
        ]
        
        pattern = ChordProgressionPattern(
            name="I-IV-V-I",
            pattern=pattern_items,
            description="Basic I-IV-V-I progression",
            tags=["common", "major"]
        )
        
        assert pattern.name == "I-IV-V-I"
        assert len(pattern.pattern) == 4
        assert pattern.tags == ["common", "major"]