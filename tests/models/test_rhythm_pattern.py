import pytest
from src.note_gen.models.rhythm_pattern import RhythmPatternData, RhythmPattern
from src.note_gen.models.rhythm_pattern import RhythmNote

import uuid


def test_validate_time_signature_valid() -> None:
    # Create pattern with valid time signature
    pattern_data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        time_signature="3/4"
    )
    assert pattern_data.time_signature == "3/4"


def test_validate_time_signature_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/0")  # Invalid denominator
    assert "Time signature denominator must be a positive power of 2" in str(exc_info.value)


def test_validate_time_signature_invalid_during_instantiation() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/")  # Invalid format
    assert "String should match pattern" in str(exc_info.value)


def test_validate_groove_type_valid() -> None:
    pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern_data.groove_type = "swing"
    assert pattern_data.groove_type == "swing"


def test_validate_groove_type_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], groove_type="invalid")
    assert "value_error" in str(exc_info.value)


def test_validate_notes_valid() -> None:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    pattern_data = RhythmPatternData(notes=valid_notes)
    assert pattern_data.notes == valid_notes


def test_validate_notes_empty() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[])
    assert "value_error" in str(exc_info.value)


def test_validate_default_duration_valid() -> None:
    pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=2.0)
    assert pattern_data.default_duration == 2.0


def test_validate_default_duration_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=0.0)
    assert "value_error" in str(exc_info.value)


def test_validate_name_valid() -> None:
    pattern = RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="4 4 4")
    assert pattern.name == "Test Pattern"


def test_validate_name_empty() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(id="1", name="", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="4 4 4")
    assert "value_error" in str(exc_info.value)


def test_validate_data_valid() -> None:
    data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern = RhythmPattern(id="1", name="Test Pattern", data=data, pattern="4 4 4")
    assert pattern.data == data


def test_validate_data_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(id="1", name="Test Pattern", data="Invalid Data", pattern="4 4 4")
    assert "Input should be a valid dictionary or instance of RhythmPatternData" in str(exc_info.value)


def test_validate_pattern_valid() -> None:
    pattern = RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="4 4 4")
    pattern.validate_pattern("4 4 4")


def test_validate_pattern_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="invalid_pattern").validate_pattern("invalid_pattern")
    assert "value_error" in str(exc_info.value)


def test_rhythm_pattern_initialization_valid() -> None:
    data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern = RhythmPattern(id="1", name="Test Pattern", data=data, pattern="1 2 3")  # Use a valid pattern
    assert pattern.name == "Test Pattern"
    assert pattern.data.notes[0].position == 0
    assert pattern.data.notes[0].duration == 1.0


def test_rhythm_pattern_initialization_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:  # Expect ValueError for invalid pattern
        RhythmPattern(id="1", name="Test Pattern", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="invalid")
    assert "value_error" in str(exc_info.value)


def test_rhythm_pattern_data_validation_notes_empty() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[], duration=1.0)
    assert "value_error" in str(exc_info.value)


def test_rhythm_note_validation_velocity_invalid(self) -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
    assert "Velocity must be between 0 and 127" in str(exc_info.value)


def test_rhythm_pattern_data_check_duration_invalid(self) -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
    assert "Duration must be a positive number" in str(exc_info.value)


def test_rhythm_pattern_creation(self) -> None:
    notes = [
        RhythmNote(
            position=0.0,
            duration=1.0,
            velocity=100,
            is_rest=False,
            accent=None,
            swing_ratio=None
        )
    ]
    data = RhythmPatternData(
        notes=notes,
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.2,
        swing_ratio=0.67,
        style="rock",
        default_duration=1.0
    )
    pattern = RhythmPattern(
        id="test_pattern",
        name="Test Pattern",
        data=data,
        description="A test rhythm pattern",
        tags=["test"],
        complexity=1.0,
        style="rock",
        pattern="1---2---3---4---"
    )
    self.assertEqual(pattern.name, "Test Pattern")
    self.assertIsNotNone(pattern.data)
    self.assertEqual(len(pattern.tags), 1)
    self.assertEqual(pattern.description, "A test rhythm pattern")
    self.assertEqual(pattern.complexity, 1.0)
    self.assertEqual(pattern.style, "rock")
    self.assertEqual(pattern.pattern, "1---2---3---4---")


def test_rhythm_note_validation_velocity_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
    assert "Velocity must be between 0 and 127" in str(exc_info.value)


def test_rhythm_pattern_data_check_duration_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
    assert "Duration must be a positive number" in str(exc_info.value)


def test_rhythm_pattern_data_initialization_empty_notes() -> None:
    with pytest.raises(ValueError, match="Notes list cannot be empty"):
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
        assert any("Invalid time signature format" in str(err["msg"]) or 
                  "String should match pattern" in str(err["msg"]) for err in errors), \
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

def test_rhythm_pattern_data_creation(self) -> None:
    notes = [
        RhythmNote(
            position=0.0,
            duration=1.0,
            velocity=100,
            is_rest=False,
            accent=None,
            swing_ratio=None
        )
    ]
    data = RhythmPatternData(
        notes=notes,
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.2,
        swing_ratio=0.67,
        style="rock",
        default_duration=1.0
    )
    self.assertEqual(data.time_signature, "4/4")
    self.assertEqual(len(data.notes), 1)
    self.assertEqual(data.style, "rock")
    self.assertFalse(data.swing_enabled)

def test_note_pattern_creation(self):
    pattern = RhythmPatternData(
        id=str(uuid.uuid4()),
        name="Test Pattern",
        notes=[RhythmNote(position=0, duration=1)],
        pattern_type="basic",
        description="Test description",
        tags=["test", "basic"],
        complexity=0.5,
        data=[1, 2, 3],
        is_test=True
    )
    self.assertEqual(pattern.name, "Test Pattern")
    self.assertIsNotNone(pattern.notes)
    self.assertEqual(len(pattern.tags), 2)

def test_rhythm_note_validation_velocity_invalid(self) -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
    assert "Velocity must be between 0 and 127" in str(exc_info.value)

def test_rhythm_pattern_data_check_duration_invalid(self) -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
    assert "Duration must be a positive number" in str(exc_info.value)