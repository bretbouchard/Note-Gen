import pytest
from note_gen.models.rhythm_pattern import RhythmPatternData
from note_gen.models.rhythm_pattern import RhythmNote
from pydantic import ValidationError
from typing import Type


def test_rhythm_pattern_data_initialization_empty_notes() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[])
        assert False, "Expected ValidationError was not raised for empty notes"
    except ValidationError as e:
        errors = e.errors()
        assert any("Notes list cannot be empty" in str(err["msg"]) for err in errors), \
            "Expected error message about empty notes not found"


def test_rhythm_pattern_data_initialization_valid_notes() -> None:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    rhythm_pattern_data = RhythmPatternData(notes=valid_notes)
    assert rhythm_pattern_data.notes == valid_notes


def test_validate_duration() -> None:
    rhythm_pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    rhythm_pattern_data.duration = 2.0
    assert rhythm_pattern_data.duration == 2.0
    print("Attempting to create RhythmPatternData with negative duration...")
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)
        print("ValueError raised as expected.")


def test_validate_duration_negative() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)


def test_validate_time_signature_invalid() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/4")
        assert False, "Expected ValidationError was not raised for invalid time signature"
    except ValidationError as e:
        errors = e.errors()
        assert any("Invalid time signature format" in str(err["msg"]) for err in errors), \
            "Expected error message about invalid time signature format not found"


def test_validate_swing_ratio_out_of_bounds() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.4, notes=[RhythmNote()])
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.8, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=1.5, notes=[RhythmNote()])
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=-0.1, notes=[RhythmNote()])


def test_recalculate_pattern_duration() -> None:
    notes = [
        RhythmNote(position=0, duration=1.0),
        RhythmNote(position=1.0, duration=1.5),
    ]
    rhythm_pattern_data = RhythmPatternData(notes=notes)
    rhythm_pattern_data.calculate_total_duration()
    print("Calculating total duration:")
    for note in notes:
        print(f"Note Position: {note.position}, Duration: {note.duration}")
    print(f"Calculated Total Duration: {rhythm_pattern_data.total_duration}")
    assert rhythm_pattern_data.total_duration == 2.5


def test_model_post_init() -> None:
    notes = [
        RhythmNote(position=0, duration=1.0),
        RhythmNote(position=1.0, duration=1.5),
    ]
    rhythm_pattern_data = RhythmPatternData(notes=notes)
    assert rhythm_pattern_data.total_duration == 2.5  # Check total_duration after initialization


def test_validate_duration_negative_2() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(duration=-1.0, notes=[])


def test_validate_swing_ratio_out_of_bounds_2() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.4, notes=[RhythmNote()])
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.8, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds_2() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=1.5, notes=[RhythmNote()])
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=-0.1, notes=[RhythmNote()])


def test_allow_empty_notes() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[])
        assert False, "Expected ValidationError was not raised for empty notes."
    except ValidationError as e:
        errors = e.errors()
        assert any("Notes list cannot be empty" in str(err["msg"]) for err in errors), \
            "Expected error message about empty notes not found"


def test_validate_duration_negative_unique() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(duration=-0.5, notes=[RhythmNote()])


def test_validate_swing_ratio_out_of_bounds_unique() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.3, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds_unique() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=2.0, notes=[RhythmNote()])


def test_validate_duration_negative_unique_2() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(duration=-1.5, notes=[RhythmNote()])


def test_validate_swing_ratio_out_of_bounds_unique_2() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.2, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds_unique_2() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=1.1, notes=[RhythmNote()])


def test_validate_duration_negative_unique_3() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(duration=-0.1, notes=[RhythmNote()])


def test_validate_swing_ratio_out_of_bounds_unique_3() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.1, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds_unique_3() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=1.2, notes=[RhythmNote()])


def test_validate_duration_negative_unique_4() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(duration=-2.5, notes=[RhythmNote()])


def test_validate_swing_ratio_out_of_bounds_unique_4() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.45, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds_unique_4() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=1.3, notes=[RhythmNote()])


def test_validate_duration_negative_unique_5() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(duration=-3.0, notes=[RhythmNote()])


def test_validate_swing_ratio_out_of_bounds_unique_5() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.35, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds_unique_5() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=1.4, notes=[RhythmNote()])


def test_validate_duration_negative_unique_6() -> None:
    with pytest.raises(ValueError, match="Duration must be positive"):
        RhythmPatternData(duration=-0.75, notes=[RhythmNote()])


def test_validate_swing_ratio_out_of_bounds_unique_6() -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75"):
        RhythmPatternData(swing_ratio=0.25, notes=[RhythmNote()])


def test_validate_humanize_amount_out_of_bounds_unique_6() -> None:
    with pytest.raises(ValueError, match="Humanize amount must be between 0 and 1"):
        RhythmPatternData(humanize_amount=1.5, notes=[RhythmNote()])
