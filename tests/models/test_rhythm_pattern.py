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
    assert "Both numerator and denominator must be positive" in str(exc_info.value)


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
    assert "Invalid groove type" in str(exc_info.value)


def test_validate_notes_valid() -> None:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    pattern_data = RhythmPatternData(notes=valid_notes)
    assert pattern_data.notes == valid_notes


def test_validate_notes_empty() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[])
    assert "List should have at least 1 item" in str(exc_info.value)


def test_validate_default_duration_valid() -> None:
    pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=2.0)
    assert pattern_data.default_duration == 2.0


def test_validate_default_duration_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=0.0)
    assert "Input should be greater than 0" in str(exc_info.value)


def test_validate_name_valid() -> None:
    pattern = RhythmPattern(
        id="1",
        name="Test Pattern",
        data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
        pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
        complexity=1.0,
        tags=["valid_tag"]
    )
    assert pattern.name == "Test Pattern"


def test_validate_name_empty() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(
            id="1",
            name="",
            data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
    assert "String should have at least 1 character" in str(exc_info.value)


def test_validate_data_valid() -> None:
    data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern = RhythmPattern(
        id="1",
        name="Test Pattern",
        data=data,
        pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
        complexity=1.0,
        tags=["valid_tag"]
    )
    assert pattern.data == data


def test_validate_data_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(
            id="1",
            name="Test Pattern",
            data="Invalid Data",
            pattern="4 4 4 4",
            complexity=1.0,
            tags=["valid_tag"]
        )
    assert "Input should be a valid dictionary or instance of RhythmPatternData" in str(exc_info.value)


def test_validate_pattern_valid() -> None:
    pattern = RhythmPattern(
        id="1",
        name="Test Pattern",
        data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
        pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
        complexity=1.0,
        tags=["valid_tag"]
    )
    assert pattern.pattern == "4 4 4 4"


def test_validate_pattern_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
            pattern="invalid_pattern",
            complexity=1.0,
            tags=["valid_tag"]
        )
    assert "Invalid pattern format" in str(exc_info.value)


def test_rhythm_pattern_initialization_valid() -> None:
    data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
    pattern = RhythmPattern(
        id="1",
        name="Test Pattern",
        data=data,
        pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
        complexity=1.0,
        tags=["valid_tag"]
    )
    assert pattern.name == "Test Pattern"
    assert pattern.pattern == "4 4 4 4"
    assert pattern.complexity == 1.0
    assert pattern.tags == ["valid_tag"]


def test_rhythm_pattern_initialization_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
            pattern="4 4 4 4",
            complexity=1.0,
            tags=[]  # Empty tags list should raise error
        )
    assert "List should have at least 1 item" in str(exc_info.value)


def test_rhythm_pattern_data_total_duration() -> None:
    notes = [
        RhythmNote(position=0, duration=1.0),
        RhythmNote(position=1.0, duration=1.0),
        RhythmNote(position=2.0, duration=1.0),
        RhythmNote(position=3.0, duration=1.0)  # Four quarter notes to total 4.0 beats
    ]
    total_duration = 4.0  # Updated to be a multiple of the default_duration
    pattern_data = RhythmPatternData(notes=notes, total_duration=total_duration, default_duration=1.0)  # Update total_duration accordingly
    # Total duration should match time signature (4/4 = 4 beats)
    assert pattern_data.total_duration == total_duration


def test_rhythm_pattern_data_initialization_empty_notes() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[])
    assert "List should have at least 1 item" in str(exc_info.value)


def test_note_pattern_creation():
    pattern = RhythmPatternData(
        id=str(uuid.uuid4()),
        notes=[RhythmNote(position=0, duration=1)],
        data=[1, 2, 3],
        is_test=True
    )
    assert pattern.notes is not None


def test_rhythm_note_validation_velocity_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
    assert "Input should be less than or equal to 127" in str(exc_info.value)


def test_rhythm_pattern_data_check_duration_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
    assert "Input should be greater than 0" in str(exc_info.value)


def test_validate_default_duration() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=-1.0)
        assert False, "Expected ValidationError was not raised for negative default duration"
    except ValidationError as e:
        errors = e.errors()
        assert any("Input should be greater than 0" in str(err["msg"]) for err in errors)


def test_validate_time_signature() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="invalid")
        assert False, "Expected ValidationError was not raised for invalid time signature"
    except ValidationError as e:
        errors = e.errors()
        assert any("String should match pattern" in str(err["msg"]) for err in errors)


def test_validate_swing_ratio() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        swing_ratio=0.5
    )
    assert data.swing_ratio == 0.5
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            swing_ratio=0.25
        )
    assert "Input should be greater than or equal to 0.5" in str(exc_info.value)


def test_validate_humanize_amount() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        humanize_amount=0.5
    )
    assert data.humanize_amount == 0.5
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            humanize_amount=1.5
        )
    assert "Input should be less than or equal to 1" in str(exc_info.value)


def test_validate_accent_pattern() -> None:
    # Test valid accent pattern
    pattern = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        accent_pattern=["0.5", "0.8"]
    )
    assert pattern.accent_pattern == ["0.5", "0.8"]
    
    # Test invalid accent pattern
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            accent_pattern=["-0.5", "2.5"]
        )
    assert "Invalid accent value. Must be a float between 0.0 and 2.0" in str(exc_info.value)


def test_validate_groove_type() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        groove_type="swing"
    )
    assert data.groove_type == "swing"
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            groove_type="invalid"
        )
    assert "Invalid groove type. Must be one of: straight, swing, shuffle" in str(exc_info.value)


def test_validate_variation_probability() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        variation_probability=0.5
    )
    assert data.variation_probability == 0.5
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            variation_probability=1.5
        )
    assert "Input should be less than or equal to 1" in str(exc_info.value)


def test_validate_notes() -> None:
    # For a non-empty case, it should pass without error:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    data = RhythmPatternData(notes=valid_notes)
    assert data.notes == valid_notes
    
    # Test empty notes case
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[])
    assert "List should have at least 1 item" in str(exc_info.value)


class TestRhythmPattern:
    def test_validate_time_signature_valid(self) -> None:
        # Create pattern with valid time signature
        pattern_data = RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            time_signature="3/4"
        )
        assert pattern_data.time_signature == "3/4"

    def test_validate_time_signature_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/0")  # Invalid denominator
        assert "Both numerator and denominator must be positive" in str(exc_info.value)

    def test_validate_time_signature_invalid_during_instantiation(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="5/")  # Invalid format
        assert "String should match pattern" in str(exc_info.value)

    def test_validate_groove_type_valid(self) -> None:
        pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
        pattern_data.groove_type = "swing"
        assert pattern_data.groove_type == "swing"

    def test_validate_groove_type_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], groove_type="invalid")
        assert "Invalid groove type" in str(exc_info.value)

    def test_validate_notes_valid(self) -> None:
        valid_notes = [RhythmNote(position=0, duration=1.0)]
        pattern_data = RhythmPatternData(notes=valid_notes)
        assert pattern_data.notes == valid_notes

    def test_validate_notes_empty(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[])
        assert "List should have at least 1 item" in str(exc_info.value)

    def test_validate_default_duration_valid(self) -> None:
        pattern_data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=2.0)
        assert pattern_data.default_duration == 2.0

    def test_validate_default_duration_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=0.0)
        assert "Input should be greater than 0" in str(exc_info.value)

    def test_validate_name_valid(self) -> None:
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.tags == ["valid_tag"]

    def test_validate_name_empty(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="",
                data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
                pattern="4 4 4 4",
                complexity=1.0,
                tags=["valid_tag"]
            )
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_validate_data_valid(self) -> None:
        data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.data == data

    def test_validate_data_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data="Invalid Data",
                pattern="4 4 4 4",
                complexity=1.0,
                tags=["valid_tag"]
            )
        assert "Input should be a valid dictionary or instance of RhythmPatternData" in str(exc_info.value)

    def test_validate_pattern_valid(self) -> None:
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        pattern.validate_pattern("4 4 4 4")

    def test_validate_pattern_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
                pattern="invalid_pattern",
                complexity=1.0,
                tags=["valid_tag"]
            ).validate_pattern("invalid_pattern")
        assert "Invalid pattern format" in str(exc_info.value)

    def test_rhythm_pattern_initialization_valid(self) -> None:
        data = RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)])
        pattern = RhythmPattern(
            id="1",
            name="Test Pattern",
            data=data,
            pattern="4 4 4 4",  # 4 quarter notes = 4 beats, matches 4/4 time signature
            complexity=1.0,
            tags=["valid_tag"]
        )
        assert pattern.name == "Test Pattern"
        assert pattern.data.notes[0].position == 0
        assert pattern.data.notes[0].duration == 1.0

    def test_rhythm_pattern_initialization_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPattern(
                id="1",
                name="Test Pattern",
                data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]),
                pattern="4 4 4 4",
                complexity=1.0,
                tags=None  # Invalid parameter
            )
        assert "Input should be a valid list" in str(exc_info.value)

    def test_rhythm_pattern_data_validation_notes_empty(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[], duration=1.0)
        assert "List should have at least 1 item" in str(exc_info.value)

    def test_rhythm_note_validation_velocity_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
        assert "Input should be less than or equal to 127" in str(exc_info.value)

    def test_rhythm_pattern_data_check_duration_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
        assert "Input should be greater than 0" in str(exc_info.value)

    def test_rhythm_pattern_creation(self) -> None:
        notes = [
            RhythmNote(
                position=0.0,
                duration=1.0,
                velocity=100,
                is_rest=False,
                accent=None,
                swing_ratio=0.67  # Set to a valid float
            )
        ]
        data = RhythmPatternData(
            notes=notes,
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.2,
            swing_ratio=0.67,
            style="rock",
            default_duration=1.0,
            total_duration=4.0  # Updated to match measure duration
        )
        pattern = RhythmPattern(
            id="test_pattern",
            name="Test Pattern",
            data=data,
            description="A test rhythm pattern",
            tags=["test"],
            complexity=1.0,
            style="rock",
            pattern="4 4 4 4"  # 4 quarter notes = 4 beats, matches 4/4 time signature
        )
        assert pattern.name == "Test Pattern"
        assert pattern.data is not None
        assert len(pattern.tags) == 1
        assert pattern.description == "A test rhythm pattern"
        assert pattern.complexity == 1.0
        assert pattern.style == "rock"
        assert pattern.pattern == "4 4 4 4"

    def test_rhythm_pattern_data_creation(self) -> None:
        notes = [
            RhythmNote(
                position=0.0,
                duration=1.0,
                velocity=100,
                is_rest=False,
                accent=None,
                swing_ratio=0.67  # Set to a valid float
            )
        ]
        pattern_data = RhythmPatternData(
            notes=notes,
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.0,
            swing_ratio=0.67,
            default_duration=1.0,
            total_duration=4.0,  # Updated to match measure duration
            accent_pattern=[],
            groove_type="straight",
            variation_probability=0.0,
            duration=1.0,
            style="basic"
        )
        assert pattern_data.time_signature == "4/4"
        assert len(pattern_data.notes) == 1
        assert pattern_data.style == "basic"
        assert not pattern_data.swing_enabled

    def test_note_pattern_creation(self):
        pattern = RhythmPatternData(
            id=str(uuid.uuid4()),
            notes=[RhythmNote(position=0, duration=1)],
            data=[1, 2, 3],
            is_test=True
        )
        assert pattern.notes is not None

    def test_rhythm_note_validation_velocity_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
        assert "Input should be less than or equal to 127" in str(exc_info.value)

    def test_rhythm_pattern_data_check_duration_invalid(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
        assert "Input should be greater than 0" in str(exc_info.value)

def test_rhythm_pattern_data_initialization_empty_notes() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[])
    assert "List should have at least 1 item" in str(exc_info.value)

def test_rhythm_pattern_data_total_duration() -> None:
    notes = [
        RhythmNote(position=0, duration=1.0),
        RhythmNote(position=1.0, duration=1.0),
        RhythmNote(position=2.0, duration=1.0),
        RhythmNote(position=3.0, duration=1.0)  # Four quarter notes to total 4.0 beats
    ]
    total_duration = 4.0  # Updated to be a multiple of the default_duration
    pattern_data = RhythmPatternData(notes=notes, total_duration=total_duration, default_duration=1.0)  # Update total_duration accordingly
    # Total duration should match time signature (4/4 = 4 beats)
    assert pattern_data.total_duration == total_duration

def test_rhythm_note_validation_velocity_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
    assert "Input should be less than or equal to 127" in str(exc_info.value)

def test_rhythm_pattern_data_check_duration_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
    assert "Input should be greater than 0" in str(exc_info.value)

def test_rhythm_pattern_creation() -> None:
    notes = [
        RhythmNote(
            position=0.0,
            duration=1.0,
            velocity=100,
            is_rest=False,
            accent=None,
            swing_ratio=0.67  # Set to a valid float
        )
    ]
    data = RhythmPatternData(
        notes=notes,
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.2,
        swing_ratio=0.67,
        style="rock",
        default_duration=1.0,
        total_duration=4.0  # Updated to match measure duration
    )
    pattern = RhythmPattern(
        id="test_pattern",
        name="Test Pattern",
        data=data,
        description="A test rhythm pattern",
        tags=["test"],
        complexity=1.0,
        style="rock",
        pattern="4 4 4 4"  # 4 quarter notes = 4 beats, matches 4/4 time signature
    )
    assert pattern.id == "test_pattern"
    assert pattern.name == "Test Pattern"
    assert pattern.data == data
    assert pattern.description == "A test rhythm pattern"
    assert pattern.tags == ["test"]
    assert pattern.complexity == 1.0
    assert pattern.style == "rock"
    assert pattern.pattern == "4 4 4 4"

def test_rhythm_pattern_data_creation() -> None:
    notes = [
        RhythmNote(
            position=0.0,
            duration=1.0,
            velocity=100,
            is_rest=False,
            accent=None,
            swing_ratio=0.67  # Set to a valid float
        )
    ]
    pattern_data = RhythmPatternData(
        notes=notes,
        time_signature="4/4",
        swing_enabled=False,
        humanize_amount=0.0,
        swing_ratio=0.67,
        default_duration=1.0,
        total_duration=4.0,  # Updated to match measure duration
        accent_pattern=[],
        groove_type="straight",
        variation_probability=0.0,
        duration=1.0,
        style="basic"
    )
    assert pattern_data.time_signature == "4/4"
    assert len(pattern_data.notes) == 1
    assert pattern_data.style == "basic"
    assert not pattern_data.swing_enabled

def test_note_pattern_creation():
    pattern = RhythmPatternData(
        id=str(uuid.uuid4()),
        notes=[RhythmNote(position=0, duration=1)],
        data=[1, 2, 3],
        is_test=True
    )
    assert pattern.notes is not None

def test_rhythm_note_validation_velocity_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=200)  # Invalid velocity
    assert "Input should be less than or equal to 127" in str(exc_info.value)

def test_rhythm_pattern_data_check_duration_invalid() -> None:
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], duration=-1.0)  # Invalid duration
    assert "Input should be greater than 0" in str(exc_info.value)

def test_validate_default_duration() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], default_duration=-1.0)
        assert False, "Expected ValidationError was not raised for negative default duration"
    except ValidationError as e:
        errors = e.errors()
        assert any("Input should be greater than 0" in str(err["msg"]) for err in errors)

def test_validate_time_signature() -> None:
    from pydantic import ValidationError
    try:
        RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)], time_signature="invalid")
        assert False, "Expected ValidationError was not raised for invalid time signature"
    except ValidationError as e:
        errors = e.errors()
        assert any("String should match pattern" in str(err["msg"]) for err in errors)

def test_validate_swing_ratio() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        swing_ratio=0.5
    )
    assert data.swing_ratio == 0.5
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            swing_ratio=0.25
        )
    assert "Input should be greater than or equal to 0.5" in str(exc_info.value)

def test_validate_humanize_amount() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        humanize_amount=0.5
    )
    assert data.humanize_amount == 0.5
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            humanize_amount=1.5
        )
    assert "Input should be less than or equal to 1" in str(exc_info.value)

def test_validate_accent_pattern() -> None:
    # Test valid accent pattern
    pattern = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        accent_pattern=["0.5", "0.8"]
    )
    assert pattern.accent_pattern == ["0.5", "0.8"]
    
    # Test invalid accent pattern
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            accent_pattern=["-0.5", "2.5"]
        )
    assert "Invalid accent value. Must be a float between 0.0 and 2.0" in str(exc_info.value)

def test_validate_groove_type() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        groove_type="swing"
    )
    assert data.groove_type == "swing"
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            groove_type="invalid"
        )
    assert "Invalid groove type. Must be one of: straight, swing, shuffle" in str(exc_info.value)

def test_validate_variation_probability() -> None:
    data = RhythmPatternData(
        notes=[RhythmNote(position=0, duration=1.0)],
        variation_probability=0.5
    )
    assert data.variation_probability == 0.5
    
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(
            notes=[RhythmNote(position=0, duration=1.0)],
            variation_probability=1.5
        )
    assert "Input should be less than or equal to 1" in str(exc_info.value)

def test_validate_notes() -> None:
    # For a non-empty case, it should pass without error:
    valid_notes = [RhythmNote(position=0, duration=1.0)]
    data = RhythmPatternData(notes=valid_notes)
    assert data.notes == valid_notes
    
    # Test empty notes case
    with pytest.raises(ValueError) as exc_info:
        RhythmPatternData(notes=[])
    assert "List should have at least 1 item" in str(exc_info.value)