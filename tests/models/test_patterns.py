import pytest
from pydantic import ValidationError
from src.note_gen.models.patterns import RhythmPattern


def test_rhythm_pattern_validation():
    # Test valid pattern
    pattern = RhythmPattern(
        name='Test Pattern',
        description='Test description',
        complexity=0.5,
        pattern='1 1 1 1',  # Changed to match 4/4 time signature
        time_signature='4/4',
        data={'beats': 4, 'subdivisions': 4}
    )
    assert pattern.pattern == '1 1 1 1'

    # Test empty pattern
    with pytest.raises(ValidationError, match='String should have at least 1 character'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=0.5,
            pattern='',
            time_signature='4/4',
            data={}
        )

    # Test invalid pattern characters
    with pytest.raises(ValidationError, match='Invalid pattern format: could not convert string to float'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=0.5,
            pattern='1a2b3',
            time_signature='4/4',
            data={}
        )


def test_time_signature_validation():
    # Test valid time signature
    pattern = RhythmPattern(
        name='Test',
        description='Test description',
        complexity=0.5,
        pattern='1 1 1',  # Changed to match 3/4 time signature
        time_signature='3/4',
        data={}
    )
    assert pattern.time_signature == '3/4'

    # Test invalid time signature format
    with pytest.raises(ValueError, match='Time signature must be in format'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=0.5,
            pattern='1 1 1',
            time_signature='invalid',
            data={}
        )

    # Test invalid denominator
    with pytest.raises(ValueError, match='Time signature denominator must be a power of 2'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=0.5,
            pattern='1 1 1',
            time_signature='4/3',
            data={}
        )
