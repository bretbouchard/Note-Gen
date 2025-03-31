import pytest
import asyncio
from src.note_gen.models.note import Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.core.enums import ScaleType, ValidationLevel, ChordQuality
from src.note_gen.generators.chord_progression_generator import ChordProgressionGenerator

@pytest.fixture
def scale_info():
    return ScaleInfo(
        key="C",
        scale_type=ScaleType.MAJOR,
        tonic=Note(pitch="C")
    )

@pytest.fixture
def generator(scale_info):
    return ChordProgressionGenerator(
        name="Test Generator",
        key="C",
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info
    )

@pytest.mark.asyncio
async def test_edge_cases(generator):
    """Test edge cases and error handling."""
    with pytest.raises(ValueError, match="Empty pattern"):
        await generator.generate_from_pattern([])

@pytest.mark.asyncio
async def test_pattern_generation_with_validation_levels(generator):
    """Test pattern generation with different validation levels."""
    pattern = [
        (1, ChordQuality.MAJOR),
        (4, ChordQuality.MAJOR),
        (5, ChordQuality.DOMINANT_SEVENTH)
    ]

    # Test strict validation
    prog_strict = await generator.generate_from_pattern(
        pattern,
        validation_level=ValidationLevel.STRICT
    )
    assert len(prog_strict.chords) == 3

@pytest.mark.asyncio
async def test_genre_patterns(generator):
    """Test genre-specific patterns."""
    for genre in ["pop", "jazz", "blues", "classical"]:
        pattern = generator.genre_patterns[genre]
        progression = await generator.generate_from_pattern(pattern)
        assert len(progression.chords) == len(pattern)

# Add similar async decorators and await calls for other test methods
