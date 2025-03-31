import pytest
from src.note_gen.services.pattern_service import PatternService
from src.note_gen.core.enums import ScaleType, ValidationLevel

@pytest.fixture
def pattern_service():
    """Return a PatternService instance."""
    return PatternService()

@pytest.mark.asyncio
async def test_generate_musical_pattern(pattern_service):
    """Test successful pattern generation."""
    pattern = await pattern_service.generate_musical_pattern(
        root_note="C",
        scale_type=ScaleType.MAJOR,
        pattern_config={
            "intervals": [0, 2, 4],
            "direction": "up",
            "octave_range": (4, 5)
        }
    )
    
    assert pattern is not None
    assert pattern.data.root_note == "C"
    assert pattern.data.scale_type == ScaleType.MAJOR

@pytest.mark.asyncio
async def test_generate_invalid_pattern(pattern_service):
    """Test pattern generation with invalid input."""
    with pytest.raises(ValueError, match="Invalid root note format"):
        await pattern_service.generate_musical_pattern(
            root_note="H",  # Invalid note name (valid notes are A-G)
            scale_type=ScaleType.MAJOR,
            pattern_config={
                "intervals": [0, 2, 4],
                "direction": "up",
                "octave_range": (4, 5)
            }
        )
