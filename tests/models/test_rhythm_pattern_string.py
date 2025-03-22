import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.models.patterns import RhythmPatternData, RhythmNote
import uuid
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_db_connection() -> AsyncMock:
    return AsyncMock()

class TestRhythmPatternString:
    async def test_rhythm_pattern_string_representation(self, mock_db_connection: AsyncMock) -> None:
        # Create a pattern with notes and rests
        pattern = RhythmPattern(
            name='Test Pattern',
            pattern=[
                {'duration': 1.0, 'velocity': 1.0},
                {'duration': 0.5, 'velocity': 0.8},
                {'duration': 0.5, 'velocity': 0.9}
            ],
            time_signature='4/4'
        )
        
        # Check string representation
        pattern_str = str(pattern)
        assert "Test Pattern" in pattern_str
        assert "4/4" in pattern_str
