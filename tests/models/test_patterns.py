import pytest
from src.note_gen.models.rhythm_pattern import RhythmPatternData
from src.note_gen.models.rhythm_pattern import RhythmNote


def test_rhythm_pattern_data_initialization_empty_notes() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        RhythmPatternData(notes=[])
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error_message = errors[0]['msg']
    assert "List should have at least 1 item after validation" in error_message


def test_rhythm_pattern_data_initialization_valid_notes() -> None:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    rhythm_pattern_data = RhythmPatternData(notes=valid_notes)
    assert rhythm_pattern_data.notes == valid_notes


def test_validate_duration() -> None:
    rhythm_pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    rhythm_pattern_data.duration = 2.0
    assert rhythm_pattern_data.duration == 2.0
    print("Attempting to create RhythmPatternData with negative duration...")
    with pytest.raises(ValueError, match="Input should be greater than 0"):  
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)
        print("ValueError raised as expected.")


def test_validate_time_signature_invalid() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/3")  # 3 is not a power of 2
        assert False, "Expected ValidationError was not raised for invalid time signature"
    except ValidationError as e:
        errors = e.errors()
        assert any("Time signature denominator must be a positive power of 2" in str(err["msg"]) for err in errors), \
            "Expected error message about invalid time signature denominator not found"


def test_validate_swing_ratio_out_of_bounds() -> None:
    with pytest.raises(ValueError, match="Input should be greater than or equal to 0.5"):
        RhythmPatternData(swing_ratio=0.4, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])
    with pytest.raises(ValueError, match="Input should be less than or equal to 0.75"):  
        RhythmPatternData(swing_ratio=0.8, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])


def test_validate_humanize_amount_out_of_bounds() -> None:
    with pytest.raises(ValueError, match="Input should be less than or equal to 1"):
        RhythmPatternData(humanize_amount=1.5, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])
    with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
        RhythmPatternData(humanize_amount=-0.1, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])


def test_recalculate_pattern_duration() -> None:
    notes = [
        RhythmNote(position=0.0, duration=2.0, velocity=100),
        RhythmNote(position=2.0, duration=2.0, velocity=100),
    ]
    rhythm_pattern_data = RhythmPatternData(notes=notes)
    rhythm_pattern_data.calculate_total_duration()
    print("Calculating total duration:")
    for note in notes:
        print(f"Note Position: {note.position}, Duration: {note.duration}")
    print(f"Calculated Total Duration: {rhythm_pattern_data.total_duration}")
    assert rhythm_pattern_data.total_duration == 4.0


def test_model_post_init() -> None:
    notes = [
        RhythmNote(position=0.0, duration=2.0, velocity=100),
        RhythmNote(position=2.0, duration=2.0, velocity=100),
    ]
    rhythm_pattern_data = RhythmPatternData(notes=notes)
    assert rhythm_pattern_data.total_duration == 4.0  # Check total_duration after initialization


def test_validate_duration_negative() -> None:
    with pytest.raises(ValueError, match="Input should be greater than 0"):  
        RhythmPatternData(duration=-1.0, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error_message = errors[0]['msg']
    assert any(re.search(r"Input should be greater than 0", error_message))


def test_validate_swing_ratio_out_of_bounds() -> None:
    with pytest.raises(ValueError, match="Input should be greater than or equal to 0.5"):
        RhythmPatternData(swing_ratio=0.4, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])
    with pytest.raises(ValueError, match="Input should be less than or equal to 0.75"):  
        RhythmPatternData(swing_ratio=0.8, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])



def test_allow_empty_notes() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        RhythmPatternData(notes=[], allow_empty_notes=False)
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error_message = errors[0]['msg']
    assert "List should have at least 1 item after validation" in error_message


def test_validate_duration_negative() -> None:
    with pytest.raises(ValueError, match="Input should be greater than 0"):
        RhythmPatternData(duration=-1.0, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])

def test_validate_swing_ratio_out_of_bounds() -> None:
    with pytest.raises(ValueError, match="Input should be greater than or equal to 0.5"):
        RhythmPatternData(swing_ratio=0.4, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])
    with pytest.raises(ValueError, match="Input should be less than or equal to 0.75"):  
        RhythmPatternData(swing_ratio=0.8, notes=[RhythmNote(position=0.0, duration=1.0, velocity=100)])



def test_rhythm_note_missing_fields() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(velocity=100)
    errors = exc_info.value.errors()
    assert len(errors) == 2
    assert any(err['type'] == 'missing' for err in errors)

def test_rhythm_note_missing_fields() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(velocity=100)
    errors = exc_info.value.errors()
    assert len(errors) == 2
    assert any(err['type'] == 'missing' for err in errors)

def test_rhythm_note_missing_duration_field() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(position=0.0, velocity=100)
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert any(err['type'] == 'missing' for err in errors)

def test_rhythm_note_missing_fields() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        RhythmPatternData(notes=[RhythmNote()])
    errors = exc_info.value.errors()
    assert len(errors) == 2
    assert any(err['type'] == 'missing' for err in errors)
