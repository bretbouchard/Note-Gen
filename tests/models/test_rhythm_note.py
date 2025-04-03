import pytest
from pydantic import ValidationError
from note_gen.models.rhythm import RhythmNote
from note_gen.core.enums import AccentType


def test_validate_velocity_valid() -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100)
    assert note.velocity == 100


def test_validate_velocity_invalid_low() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(position=0.0, duration=1.0, velocity=-1)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'greater_than_equal'
    assert errors[0]['loc'] == ('velocity',)


def test_validate_groove_offset_invalid_high() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=100, groove_offset=1.5)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'less_than_equal'
    assert errors[0]['loc'] == ('groove_offset',)


def test_validate_groove_offset_invalid_low() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=100, groove_offset=-1.5)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'greater_than_equal'
    assert errors[0]['loc'] == ('groove_offset',)


def test_validate_groove_offset_valid_min() -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, groove_offset=-1.0)
    assert note.groove_offset == -1.0


def test_validate_groove_offset_valid_max() -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, groove_offset=1.0)
    assert note.groove_offset == 1.0


def test_rhythm_note_creation():
    note = RhythmNote(position=0.0, duration=1.0, velocity=64)
    assert note.position == 0.0
    assert note.duration == 1.0
    assert note.velocity == 64


def test_rhythm_note_validation():
    with pytest.raises(ValidationError):
        RhythmNote(position=-1.0, duration=1.0, velocity=64)


def test_rhythm_note_velocity_validation():
    with pytest.raises(ValidationError):
        RhythmNote(position=0.0, duration=1.0, velocity=128)
