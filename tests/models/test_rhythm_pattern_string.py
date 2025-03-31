import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote
import uuid
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_db_connection() -> AsyncMock:
    return AsyncMock()

@pytest.mark.asyncio
async def test_rhythm_pattern_string_representation(mock_db_connection: AsyncMock) -> None:
    # Create a pattern with notes and rests
    pattern = RhythmPattern(
        name="Test Pattern",
        time_signature=(4, 4),  # Changed to tuple format
        pattern=[
            RhythmNote(**{
                "position": 0.0,
                "duration": 1.0,
                "velocity": 64,
                "accent": False,
                "tuplet_ratio": (1, 1),
                "groove_offset": 0.0,
                "groove_velocity": 1.0
            }),
            RhythmNote(**{
                "position": 1.0,
                "duration": 0.5,
                "velocity": 51,
                "accent": False,
                "tuplet_ratio": (1, 1),
                "groove_offset": 0.0,
                "groove_velocity": 1.0
            }),
            RhythmNote(**{
                "position": 1.5,
                "duration": 0.5,
                "velocity": 58,
                "accent": False,
                "tuplet_ratio": (1, 1),
                "groove_offset": 0.0,
                "groove_velocity": 1.0
            })
        ]
    )
    
    # Check string representation
    pattern_str = str(pattern)
    assert "Test Pattern" in pattern_str
    assert "4/4" in pattern_str  # Still check for "4/4" in string representation
