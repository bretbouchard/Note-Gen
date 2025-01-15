import pytest
from note_gen.models.rhythm_pattern import RhythmPatternData, RhythmPattern
from note_gen.models.rhythm_pattern import RhythmNote


def test_validate_time_signature_valid():
    pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern_data.time_signature = "3/4"
    assert pattern_data.time_signature == "3/4"


def test_validate_time_signature_invalid():
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/4")
    assert "Invalid time signature. Must be in format: numerator/denominator where numerator is one of [2, 3, 4, 6, 8, 9, 12] and denominator is a power of 2" in str(exc_info.value)


def test_validate_groove_type_valid():
    pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern_data.groove_type = "swing"
    assert pattern_data.groove_type == "swing"


def test_validate_groove_type_invalid():
    with pytest.raises(ValueError, match="Groove type must be either 'straight' or 'swing'"):
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], groove_type="invalid")


def test_validate_notes_valid():
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    pattern_data = RhythmPatternData(notes=valid_notes)
    assert pattern_data.notes == valid_notes


def test_validate_notes_empty():
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[])
    assert "Notes list cannot be empty" in str(exc_info.value)


def test_validate_default_duration_valid():
    pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=2.0)
    assert pattern_data.default_duration == 2.0


def test_validate_default_duration_invalid():
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=0.0)
    assert "Default duration must be positive" in str(exc_info.value)


def test_validate_name_valid():
    pattern = RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="4 4 4")
    assert pattern.name == "Test Pattern"


def test_validate_name_empty():
    with pytest.raises(ValueError, match="Name cannot be empty."):
        RhythmPattern(id="1", name="", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="4 4 4")


def test_validate_data_valid():
    data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern = RhythmPattern(id="1", name="Test Pattern", data=data, pattern="4 4 4")
    assert pattern.data == data


def test_validate_data_invalid():
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(id="1", name="Test Pattern", data="Invalid Data", pattern="4 4 4")
    assert "Input should be a valid dictionary or instance of RhythmPatternData" in str(exc_info.value)


def test_validate_pattern_valid():
    pattern = RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="4 4 4")
    pattern.validate_pattern("4 4 4")


def test_validate_pattern_invalid():
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="invalid_pattern").validate_pattern("invalid_pattern")
    assert "Pattern can only contain numbers 1-9, dots (.), hyphens (-), and spaces." in str(exc_info.value)


def test_rhythm_pattern_initialization_valid():
    data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern = RhythmPattern(id="1", name="Test Pattern", data=data, pattern="1 2 3")  # Use a valid pattern
    assert pattern.name == "Test Pattern"
    assert pattern.data.notes[0].position == 0
    assert pattern.data.notes[0].duration == 1.0


def test_rhythm_pattern_initialization_invalid():
    with pytest.raises(ValueError):  # Expect ValueError for invalid pattern
        RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="invalid")


def test_rhythm_pattern_data_validation_notes_empty():
    with pytest.raises(ValueError):
        RhythmPatternData(notes=[], duration=1.0)


def test_rhythm_note_validation_velocity_invalid():
    with pytest.raises(ValueError):
        RhythmNote(position=0, duration=1.0, velocity=200)


def test_rhythm_pattern_data_check_duration_invalid():
    with pytest.raises(ValueError):
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)