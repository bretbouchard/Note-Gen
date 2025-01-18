import pytest
from src.note_gen.models.rhythm_pattern import RhythmNote


def test_validate_velocity_valid(self) -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100)
    assert note.velocity == 100


def test_validate_velocity_invalid_low(self) -> None:
    with pytest.raises(ValueError, match="Velocity must be between 0 and 127."):
        RhythmNote(position=0, duration=1.0, velocity=-1)


def test_validate_velocity_invalid_high(self) -> None:
    with pytest.raises(ValueError, match="Velocity must be between 0 and 127."):
        RhythmNote(position=0, duration=1.0, velocity=128)


def test_validate_swing_ratio_valid(self) -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.6)
    assert note.swing_ratio == 0.6


def test_validate_swing_ratio_invalid(self) -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75."):
        RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.8)


def test_validate_swing_ratio_invalid_low(self) -> None:
    with pytest.raises(ValueError, match="Swing ratio must be between 0.5 and 0.75."):
        RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.4)


def test_validate_swing_ratio_valid_min(self) -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.5)
    assert note.swing_ratio == 0.5


def test_validate_swing_ratio_valid_max(self) -> None:
    note = RhythmNote(position=0, duration=1.0, velocity=100, swing_ratio=0.75)
    assert note.swing_ratio == 0.75
