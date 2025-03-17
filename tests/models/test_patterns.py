import pytest
from src.note_gen.models.patterns import RhythmPattern


def test_rhythm_pattern_validation():
    # Test valid pattern
    pattern = RhythmPattern(
        name='Test Pattern',
        description='Test description',
        complexity=3,
        pattern='1-2-3',
        time_signature='4/4',
        data={'beats': 4, 'subdivisions': 4}
    )
    assert pattern.pattern == '1-2-3'

    # Test empty pattern
    with pytest.raises(ValueError, match='Pattern cannot be empty'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=3,
            pattern='',
            time_signature='4/4',
            data={}
        )

    # Test invalid pattern characters
    with pytest.raises(ValueError, match='Pattern must contain only numbers and hyphens for rests'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=3,
            pattern='1a2b3',
            time_signature='4/4',
            data={}
        )


def test_time_signature_validation():
    # Test valid time signature
    pattern = RhythmPattern(
        name='Test',
        description='Test description',
        complexity=3,
        pattern='1-2-3',
        time_signature='3/4',
        data={}
    )
    assert pattern.time_signature == '3/4'

    # Test invalid time signature format
    with pytest.raises(ValueError, match='String should match pattern'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=3,
            pattern='1-2-3',
            time_signature='invalid',
            data={}
        )

    # Test invalid denominator
    with pytest.raises(ValueError, match='Denominator must be 2, 4, 8, or 16'):
        RhythmPattern(
            name='Test',
            description='Test description',
            complexity=3,
            pattern='1-2-3',
            time_signature='4/3',
            data={}
        )
