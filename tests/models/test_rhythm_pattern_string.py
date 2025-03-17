import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.patterns import RhythmPattern, RhythmPatternData, RhythmNote
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
            id=str(uuid.uuid4()),
            name="Test Pattern",
            data=RhythmPatternData(
                notes=[
                    RhythmNote(position=0, duration=1.0, is_rest=False, velocity=100),
                    RhythmNote(position=1.0, duration=1.0, is_rest=True, velocity=0),
                    RhythmNote(position=2.0, duration=2.0, is_rest=False, velocity=100)
                ],
                time_signature="4/4",
                default_duration=1.0,
                groove_type="straight",
                style="jazz",
                duration=4.0
            ),
            pattern="1 -1 2",
            description="Test pattern with notes and rests",
            tags=["test"],
            complexity=1.0
        )
        
        # Check string representation
        pattern_str = str(pattern)
        assert "Test Pattern" in pattern_str
        assert "1 -1 2" in pattern_str
        assert "4/4" in pattern_str
        assert "straight" in pattern_str
        assert "jazz" in pattern_str
        assert "test" in pattern_str
        assert "1.0" in pattern_str  # complexity
        assert "4.0" in pattern_str  # duration
