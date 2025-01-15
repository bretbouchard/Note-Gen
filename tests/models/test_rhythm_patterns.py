import pytest
from note_gen.models.rhythm_pattern import RhythmPatternData, RhythmNote
import random
import logging

def test_rhythm_pattern_data_initialization_empty_notes() -> None:
    with pytest.raises(ValueError, match="Notes cannot be empty."):
        RhythmPatternData(notes=[])

def test_rhythm_pattern_data_total_duration() -> None:
    notes = [
        RhythmNote(position=0, duration=1.0),
        RhythmNote(position=1.0, duration=1.5),
    ]
    pattern_data = RhythmPatternData(notes=notes)
    assert pattern_data.total_duration == 2.5

def test_validate_default_duration() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=-1.0)
        assert False, "Expected ValidationError was not raised for negative default duration"
    except ValidationError as e:
        errors = e.errors()
        assert any("Default duration must be positive" in str(err["msg"]) for err in errors), \
            "Expected error message about negative default duration not found"

def test_validate_time_signature() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="invalid")
        assert False, "Expected ValidationError was not raised for invalid time signature"
    except ValidationError as e:
        errors = e.errors()
        assert any("Invalid time signature format" in str(err["msg"]) for err in errors), \
            "Expected error message about invalid time signature format not found"

def test_validate_swing_ratio() -> None:
    assert RhythmPatternData.validate_swing_ratio(0.5) == 0.5
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData.validate_swing_ratio(0.25)
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData.validate_swing_ratio(0.8)

def test_validate_humanize_amount() -> None:
    assert RhythmPatternData.validate_humanize_amount(0.5) == 0.5
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData.validate_humanize_amount(1.5)

def test_validate_accent_pattern() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], accent_pattern=["strong", "weak"])
        assert False, "Expected ValidationError was not raised for invalid accent pattern"
    except ValidationError as e:
        errors = e.errors()
        assert any("Accent values must be floats between 0 and 1" in str(err["msg"]) for err in errors), \
            "Expected error message about invalid accent values not found"

    # Test valid accent pattern
    pattern = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], accent_pattern=[0.5, 0.8])
    assert pattern.accent_pattern == [0.5, 0.8]

def test_validate_groove_type() -> None:
    assert RhythmPatternData.validate_groove_type("swing") == "swing"
    with pytest.raises(ValueError, match="Groove type must be either 'straight' or 'swing'"):
        RhythmPatternData.validate_groove_type("invalid")

def test_validate_variation_probability() -> None:
    assert RhythmPatternData.validate_variation_probability(0.5) == 0.5
    with pytest.raises(ValueError, match="Variation probability must be between 0 and 1"):
        RhythmPatternData.validate_variation_probability(1.5)

def test_validate_notes() -> None:
    # For a non-empty case, it should pass without error:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    assert RhythmPatternData.validate_notes(valid_notes) == valid_notes

    # Test empty notes case
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[])
        assert False, "Expected ValidationError was not raised for empty notes"
    except ValidationError as e:
        errors = e.errors()
        assert any("Notes list cannot be empty" in str(err["msg"]) for err in errors), \
            "Expected error message about empty notes not found"