"""Test pattern generator functionality."""
import pytest
from note_gen.core.sequence_generator import PatternGenerator
from note_gen.core.enums import PatternDirection, ScaleType, ValidationLevel, PatternType

@pytest.fixture
def generator():
    return PatternGenerator()

def test_generate_note_pattern(generator):
    pattern_config = {
        'root_note': "C",
        'scale_type': ScaleType.MAJOR,
        'intervals': [0, 2, 4],
        'direction': PatternDirection.UP,
        'octave_range': (4, 5)
    }

    pattern = generator.generate_pattern(
        pattern_type=PatternType.MELODIC,
        config=pattern_config,
        validation_level=ValidationLevel.NORMAL
    )
    
    assert pattern is not None
    assert len(pattern.pattern) > 0

def test_generate_invalid_note_pattern(generator):
    # Test with invalid intervals
    pattern_config = {
        'root_note': "C",
        'scale_type': ScaleType.MAJOR,
        'intervals': [-1, 100],  # Invalid intervals
        'direction': PatternDirection.UP,
        'octave_range': (4, 5)
    }

    with pytest.raises(ValueError):
        generator.generate_pattern(
            pattern_type=PatternType.MELODIC,
            config=pattern_config,
            validation_level=ValidationLevel.NORMAL
        )

def test_generate_rhythm_pattern(generator):
    pattern_config = {
        'durations': [1.0, 0.5, 0.5, 1.0],
        'time_signature': (4, 4)
    }

    pattern = generator.generate_pattern(
        pattern_type=PatternType.RHYTHMIC,
        config=pattern_config,
        validation_level=ValidationLevel.NORMAL
    )
    
    assert pattern is not None
    assert len(pattern.pattern) > 0

def test_generate_invalid_rhythm_pattern(generator):
    # Test with invalid durations (sum > time signature)
    pattern_config = {
        'durations': [2.0, 2.0, 2.0],  # 6 beats total in 4/4 time
        'time_signature': (4, 4)
    }

    with pytest.raises(ValueError):
        generator.generate_pattern(
            pattern_type=PatternType.RHYTHMIC,
            config=pattern_config,
            validation_level=ValidationLevel.NORMAL
        )
