"""Tests for the request models."""

import pytest
from note_gen.models.request_models import (
    GenerateSequenceRequest,
    GenerateRequest,
    GenerateResponse,
    ErrorModel,
    StatusResponse
)
from note_gen.models.scale_info import ScaleInfo
from note_gen.core.enums import ScaleType

def test_generate_sequence_request():
    """Test the GenerateSequenceRequest model."""
    # Create a valid request
    request = GenerateSequenceRequest(
        note_pattern_name="Simple Triad",
        rhythm_pattern_name="Basic Rhythm",
        progression_name="I-IV-V-I",
        scale_info=ScaleInfo(key="C", scale_type=ScaleType.MAJOR)
    )

    # Test default values
    assert request.tempo == 120  # Default BPM
    assert request.time_signature == (4, 4)  # Default time signature
    assert request.key == "C"  # Default key

    # Test custom values
    custom_request = GenerateSequenceRequest(
        note_pattern_name="Simple Triad",
        rhythm_pattern_name="Basic Rhythm",
        progression_name="I-IV-V-I",
        scale_info=ScaleInfo(key="F#", scale_type=ScaleType.MINOR),
        tempo=140,
        time_signature=(3, 4),
        key="F#",
        duration=16.0
    )

    assert custom_request.tempo == 140
    assert custom_request.time_signature == (3, 4)
    assert custom_request.key == "F#"
    assert custom_request.duration == 16.0
    assert custom_request.scale_info.key == "F#"
    assert custom_request.scale_info.scale_type == ScaleType.MINOR

def test_generate_sequence_request_validation():
    """Test validation in the GenerateSequenceRequest model."""
    # Missing required fields should raise an error
    with pytest.raises(Exception):
        GenerateSequenceRequest(
            note_pattern_name="Simple Triad",
            rhythm_pattern_name="Basic Rhythm"
            # Missing progression_name and scale_info
        )
