import pytest
from src.note_gen.models.rhythm_pattern import RhythmPatternData, RhythmNote

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
    # Directly test the validator method
    assert RhythmPatternData.validate_default_duration(1.0) == 1.0
    with pytest.raises(ValueError, match="Default duration must be a positive float."):
        RhythmPatternData.validate_default_duration(-1.0)

def test_validate_time_signature() -> None:
    assert RhythmPatternData.validate_time_signature("4/4") == "4/4"
    with pytest.raises(ValueError, match="Invalid time signature"):
        RhythmPatternData.validate_time_signature("5/4")

def test_validate_swing_ratio() -> None:
    assert RhythmPatternData.validate_swing_ratio(0.5) == 0.5
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75."):
        RhythmPatternData.validate_swing_ratio(0.25)
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75."):
        RhythmPatternData.validate_swing_ratio(0.8)

def test_validate_humanize_amount() -> None:
    assert RhythmPatternData.validate_humanize_amount(0.5) == 0.5
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1. Invalid value found."):
        RhythmPatternData.validate_humanize_amount(1.5)

def test_validate_accent_pattern() -> None:
    valid = RhythmPatternData.validate_accent_pattern(["strong", "weak"])
    assert valid == ["strong", "weak"]
    with pytest.raises(ValueError, match="Accent pattern must be a list of strings"):
        RhythmPatternData.validate_accent_pattern([1, 2])

def test_validate_groove_type() -> None:
    assert RhythmPatternData.validate_groove_type("swing") == "swing"
    with pytest.raises(ValueError, match="Groove type must be either 'straight' or 'swing'"):
        RhythmPatternData.validate_groove_type("invalid")

def test_validate_variation_probability() -> None:
    assert RhythmPatternData.validate_variation_probability(0.5) == 0.5
    with pytest.raises(ValueError, match="Variation probability must be between 0 and 1"):
        RhythmPatternData.validate_variation_probability(1.5)

def test_validate_notes() -> None:
    # Since our model's field validator for notes raises an error on empty list,
    # we directly call that validator.
    with pytest.raises(ValueError, match="Notes cannot be empty."):
        RhythmPatternData.validate_notes([])

    # For a non-empty case, it should pass without error:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    assert RhythmPatternData.validate_notes(valid_notes) == valid_notes