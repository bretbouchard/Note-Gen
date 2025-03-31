import pytest
from unittest.mock import AsyncMock
from pydantic import ValidationError
from src.note_gen.models.patterns import RhythmPattern
from src.note_gen.models.rhythm import RhythmNote

@pytest.fixture
def mock_db_connection() -> AsyncMock:
    return AsyncMock()

class TestRhythmPatternValidation:
    @pytest.mark.asyncio
    async def test_validate_swing_ratio_out_of_bounds(self, mock_db_connection):
        """Test swing ratio validation."""
        # Test lower bound
        with pytest.raises(ValidationError):
            RhythmPattern(
                name="Test Pattern",
                pattern=[RhythmNote(position=0.0, duration=1.0)],
                swing_ratio=0.4  # Below minimum of 0.5
            )

    @pytest.mark.asyncio
    async def test_validate_humanize_amount_out_of_bounds(self, mock_db_connection):
        """Test humanize amount validation."""
        # Test upper bound
        with pytest.raises(ValidationError):
            RhythmPattern(
                name="Test Pattern",
                pattern=[RhythmNote(position=0.0, duration=1.0)],
                humanize_amount=0.2  # Above maximum of 0.1
            )
