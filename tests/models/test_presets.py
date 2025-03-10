import pytest
from unittest.mock import patch
from src.note_gen.models.presets import Presets
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.patterns import COMMON_PROGRESSIONS, NOTE_PATTERNS, RHYTHM_PATTERNS

@patch('src.note_gen.models.presets.Presets.load')
def test_preset_initialization(mock_load) -> None:
    mock_load.return_value = [Presets()]  # Mock the load method to return a list of Presets
    preset = Presets()  # Instantiate the Presets model
    assert preset.common_progressions == COMMON_PROGRESSIONS

@patch('src.note_gen.models.presets.Presets.load')
def test_load_presets(mock_load) -> None:
    mock_load.return_value = [Presets()]  # Mock the load method to return a list of Presets
    presets = Presets.load()  # Use the load method to retrieve presets
    assert len(presets) > 0  # Ensure presets are loaded
    for preset in presets:
        assert isinstance(preset, Presets)  # Ensure each loaded item is a Presets instance
        assert preset.common_progressions == COMMON_PROGRESSIONS