from __future__ import annotations
import pytest
from src.note_gen.models.patterns import RhythmNote
from pydantic_core import ValidationError


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


def test_validate_velocity_invalid_high() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=128)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'less_than_equal'
    assert errors[0]['loc'] == ('velocity',)


def test_validate_swing_ratio_valid() -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.6)
    assert note.swing_ratio == 0.6


def test_validate_swing_ratio_invalid() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.8)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'less_than_equal'
    assert errors[0]['loc'] == ('swing_ratio',)


def test_validate_swing_ratio_invalid_low() -> None:
    with pytest.raises(ValidationError) as exc_info:
        RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.4)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['type'] == 'greater_than_equal'
    assert errors[0]['loc'] == ('swing_ratio',)


def test_validate_swing_ratio_valid_min() -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.5)
    assert note.swing_ratio == 0.5


def test_validate_swing_ratio_valid_max() -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.75)
    assert note.swing_ratio == 0.75
