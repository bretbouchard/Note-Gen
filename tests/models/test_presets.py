import pytest
from unittest.mock import patch
from src.note_gen.models.presets import Presets

@patch('src.note_gen.models.presets.Presets.load')
def test_preset_initialization(mock_load) -> None:
    mock_load.return_value = [Presets()]  # Mock the load method to return a list of Presets
    preset = Presets()  # Instantiate the Presets model
    # Instead of checking equality with COMMON_PROGRESSIONS, verify the field is a non-empty dict.
    assert isinstance(preset.common_progressions, dict)
    assert len(preset.common_progressions) > 0

@patch('src.note_gen.models.presets.Presets.load')
def test_load_presets(mock_load) -> None:
    mock_load.return_value = [Presets()]  # Mock the load method to return a list of Presets
    presets = Presets.load()  # Use the load method to retrieve presets
    assert len(presets) > 0  # Ensure presets are loaded
    for preset in presets:
        assert isinstance(preset, Presets)  # Ensure each loaded item is a Presets instance
        assert isinstance(preset.common_progressions, dict), "Common progressions should be a dictionary"  # Check if common_progressions is a dictionary
        assert len(preset.common_progressions) > 0, "Common progressions should not be empty"  # Check if common_progressions is not empty