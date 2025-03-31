"""Tests for the pattern generator."""
import pytest
from note_gen.core.sequence_generator import PatternGenerator
from src.note_gen.core.enums import ScaleType, PatternDirection, ValidationLevel

@pytest.fixture
def generator():
    return PatternGenerator()

def test_generate_note_pattern(generator):
    pattern_config = {
        'intervals': [0, 2, 4],
        'direction': PatternDirection.UP,
        'octave_range': (4, 5)
    }
    
    pattern = generator.generate_note_pattern(
        root_note="C",
        scale_type=ScaleType.MAJOR,
        pattern_config=pattern_config,
        validation_level=ValidationLevel.NORMAL
    )
    
    assert pattern is not None
    assert pattern.data.root_note == "C"
    assert pattern.data.scale_type == ScaleType.MAJOR
    assert pattern.data.intervals == [0, 2, 4]

def test_generate_invalid_note_pattern(generator):
    # Test with invalid intervals
    pattern_config = {
        'intervals': [-1, 100],  # Invalid intervals
        'direction': PatternDirection.UP,
        'octave_range': (4, 5)
    }
    
    pattern = generator.generate_note_pattern(
        root_note="C",
        scale_type=ScaleType.MAJOR,
        pattern_config=pattern_config,
        validation_level=ValidationLevel.NORMAL
    )
    
    assert pattern is None

def test_generate_rhythm_pattern(generator):
    pattern = generator.generate_rhythm_pattern(
        durations=[1.0, 0.5, 0.5, 1.0],
        time_signature=(4, 4),
        validation_level=ValidationLevel.NORMAL
    )
    
    assert pattern is not None
    assert pattern.durations == [1.0, 0.5, 0.5, 1.0]
    assert pattern.time_signature == (4, 4)

def test_generate_invalid_rhythm_pattern(generator):
    # Test with invalid durations (sum > time signature)
    pattern = generator.generate_rhythm_pattern(
        durations=[2.0, 2.0, 2.0],  # 6 beats total in 4/4 time
        time_signature=(4, 4),
        validation_level=ValidationLevel.NORMAL
    )
    
    assert pattern is None