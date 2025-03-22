import pytest
from unittest.mock import patch
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.models.presets import Presets, Patterns
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.patterns import COMMON_PROGRESSIONS, NOTE_PATTERNS, ValidationError, RhythmPatternData
from src.note_gen.core.enums import ScaleType
from pydantic import BaseModel, ConfigDict

@patch('src.note_gen.models.presets.Presets.load')
def test_preset_initialization(mock_load) -> None:
    mock_load.return_value = [Presets()]
    presets = Presets.load()[0]
    
    # Verify default patterns are initialized
    assert isinstance(presets.patterns, Patterns)
    assert 'Simple Triad' in presets.patterns.note_patterns
    assert 'basic_4_4' in presets.patterns.rhythm_patterns
    
    # Verify RhythmPattern initialization
    rhythm_pattern = presets.patterns.rhythm_patterns['basic_4_4']
    assert rhythm_pattern.pattern == '1 1 1 1'
    assert rhythm_pattern.data is not None
    
    # Verify NotePattern initialization
    note_pattern = presets.patterns.note_patterns['Simple Triad']
    assert note_pattern.intervals == [0, 4, 7]
    assert note_pattern.data.scale_type == ScaleType.MAJOR
    assert note_pattern.data.root_note == "C"
    assert note_pattern.data.octave_range == [4, 5]
    assert note_pattern.data.max_interval_jump == 12
    assert note_pattern.data.allow_chromatic == False
    assert note_pattern.data.direction == "up"
    
    # Test invalid pattern - should fail validation
    with pytest.raises(ValidationError):
        RhythmPattern(
            name='invalid',
            pattern=[],  # Empty list should trigger validation error
            time_signature="4/4",
            description='Test description',
            complexity=0.5,
            data={}
        )

@patch('src.note_gen.models.presets.Presets.load')
def test_load_presets(mock_load) -> None:
    mock_load.return_value = Presets(
        default_key='C',
        default_scale_type=ScaleType.MAJOR
    )
    presets = Presets.load()
    assert len(presets) > 0
    for preset in presets:
        assert isinstance(preset, Presets)
        assert preset.common_progressions == COMMON_PROGRESSIONS
