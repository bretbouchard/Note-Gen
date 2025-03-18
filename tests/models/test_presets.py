import pytest
from unittest.mock import patch
from src.note_gen.models.presets import Presets, Patterns
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.patterns import COMMON_PROGRESSIONS, NOTE_PATTERNS, RhythmPattern, RhythmPatternData, ValidationError

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
    assert note_pattern.data.notes[0].note_name == 'C'
    
    # Test invalid pattern - should fail validation
    with pytest.raises(ValidationError):
        RhythmPattern(
            name='invalid',
            pattern='invalid pattern',  # This should trigger validation error
            data=RhythmPatternData(
                pattern="4 4 4 4",  # Valid pattern string
                duration=1.0,
                position=0.0,
                velocity=100,
                style="basic",
                groove_type="straight",
                time_signature="4/4",  # Added required field
                default_duration=1.0,
                notes=[],  # Added required field
                accent_pattern=[1.0, 1.0, 1.0, 1.0]  # Added required field
            )
        )

@patch('src.note_gen.models.presets.Presets.load')
def test_load_presets(mock_load) -> None:
    mock_load.return_value = [Presets()]
    presets = Presets.load()
    assert len(presets) > 0
    for preset in presets:
        assert isinstance(preset, Presets)
        assert preset.common_progressions == COMMON_PROGRESSIONS