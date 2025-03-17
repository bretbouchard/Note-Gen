import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.patterns import RhythmPatternData, RhythmNote

@pytest.fixture
def mock_db_connection() -> AsyncMock:
    return AsyncMock()

class TestRhythmPatternValidation:
    async def test_validate_swing_ratio_out_of_bounds(self, mock_db_connection: AsyncMock) -> None:
        # Test lower bound
        with pytest.raises(ValueError, match="Input should be greater than or equal to 0.5"):
            RhythmPatternData(
                notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)],
                swing_ratio=0.4
            )
        
        # Test upper bound
        with pytest.raises(ValueError, match="Input should be less than or equal to 0.75"):
            RhythmPatternData(
                notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)],
                swing_ratio=0.8
            )

    async def test_validate_humanize_amount_out_of_bounds(self, mock_db_connection: AsyncMock) -> None:
        # Test upper bound
        with pytest.raises(ValueError, match="Input should be less than or equal to 1"):
            RhythmPatternData(
                notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)],
                humanize_amount=1.5
            )
        
        # Test lower bound
        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            RhythmPatternData(
                notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)],
                humanize_amount=-0.1
            )
