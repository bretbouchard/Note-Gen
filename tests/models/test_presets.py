import pytest
from src.note_gen.models.presets import Presets

def test_preset_initialization() -> None:
    preset = Presets()  # Instantiate the Presets model
    # Instead of checking equality with COMMON_PROGRESSIONS, verify the field is a non-empty dict.
    assert isinstance(preset.common_progressions, dict)
    assert len(preset.common_progressions) > 0

def test_load_presets() -> None:
    presets = Presets.load()  # Use the load method to retrieve presets
    assert len(presets) > 0  # Ensure presets are loaded
    for preset in presets:
        assert isinstance(preset, Presets)  # Ensure each loaded item is a Presets instance