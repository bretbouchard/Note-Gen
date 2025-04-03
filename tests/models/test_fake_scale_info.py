"""Tests for the FakeScaleInfo model."""

import pytest
from note_gen.models.fake_scale_info import FakeScaleInfo
from note_gen.models.note import Note
from note_gen.core.enums import ScaleType

def test_fake_scale_info_basic():
    """Test basic fake scale info functionality."""
    fake_scale = FakeScaleInfo(
        key="C4",
        scale_type=ScaleType.MAJOR,
        complexity=0.5
    )
    
    # Test basic properties
    assert fake_scale.get_note_display_name("C4") == "C4"
    assert fake_scale.root == "C"
    assert fake_scale.type == ScaleType.MAJOR

def test_fake_scale_info_complex():
    """Test more complex fake scale info scenarios."""
    fake_scale = FakeScaleInfo(
        key="F#4",
        scale_type=ScaleType.MINOR,
        complexity=0.7
    )
    
    # Test properties
    assert fake_scale.complexity == 0.7
    assert fake_scale.root == "F#"
    assert fake_scale.root == "F#"

def test_fake_scale_info_get_scale_notes():
    """Test getting scale notes from fake scale info."""
    # Test major scale
    fake_scale = FakeScaleInfo(
        key="C4",
        scale_type=ScaleType.MAJOR,
        complexity=1.0
    )
    notes = fake_scale.get_scale_notes()
    assert len(notes) > 0
    # Since notes are returned as strings, test the first note directly
    assert notes[0] == "C"  # First note should be root note

def test_fake_scale_info_invalid_input():
    """Test invalid input handling."""
    with pytest.raises(ValueError, match="Invalid key format"):
        FakeScaleInfo(
            key="H4",
            scale_type=ScaleType.MAJOR,
            complexity=1.0  # Added required complexity field
        )
    
    fake_scale = FakeScaleInfo(
        key="C4",
        scale_type=ScaleType.MAJOR,
        complexity=1.0  # Added required complexity field
    )
    assert fake_scale.key == "C4"
