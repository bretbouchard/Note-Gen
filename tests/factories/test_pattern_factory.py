import pytest
from src.note_gen.factories.pattern_factory import PatternFactory
from src.note_gen.core.enums import ScaleType, PatternDirection
from src.note_gen.models.patterns import NotePattern, RhythmPattern

@pytest.fixture
def pattern_factory():
    return PatternFactory()

def test_create_note_pattern(pattern_factory):
    pattern = pattern_factory.create_note_pattern(
        root_note="C",
        scale_type=ScaleType.MAJOR,
        intervals=[0, 2, 4, 5, 7],
        direction=PatternDirection.UP,
        octave_range=(4, 5)
    )
    
    assert isinstance(pattern, NotePattern)
    assert pattern.data.root_note == "C"
    assert pattern.data.scale_type == ScaleType.MAJOR
    assert pattern.data.intervals == [0, 2, 4, 5, 7]

def test_create_rhythm_pattern(pattern_factory):
    pattern = pattern_factory.create_rhythm_pattern(
        durations=[1.0, 0.5, 0.5, 1.0],
        time_signature=(4, 4)
    )
    
    assert isinstance(pattern, RhythmPattern)
    assert pattern.durations == [1.0, 0.5, 0.5, 1.0]
    assert pattern.time_signature == (4, 4)