import pytest
from src.note_gen.populate_db import format_chord_progression
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.presets import Presets

@pytest.mark.asyncio
async def test_format_chord_progression_valid():
    from src.note_gen.models.patterns import Patterns
    COMMON_PROGRESSIONS = Patterns.COMMON_PROGRESSIONS
    progression_name = "I-IV-V"
    roman_progression = ["I", "IV", "V"]
    expected_output = {
        'id': str,
        'name': progression_name,
        'scale_info': {
            'root': {'note_name': 'C', 'octave': 4},
            'scale_type': 'MAJOR'
        },
        'chords': [
            {'root': {'note_name': 'C', 'octave': 4}, 'quality': ChordQuality.MAJOR},
            {'root': {'note_name': 'F', 'octave': 4}, 'quality': ChordQuality.MAJOR},
            {'root': {'note_name': 'G', 'octave': 4}, 'quality': ChordQuality.MAJOR},
        ],
        'key': 'C',
        'scale_type': 'MAJOR',
        'description': f'Progression: {progression_name}',
        'tags': ['preset'],
        'complexity': 1.0,
        'is_test': False
    }

    result = await format_chord_progression(progression_name, roman_progression)
    assert result['name'] == expected_output['name']
    assert len(result['chords']) == len(expected_output['chords'])


@pytest.mark.asyncio
async def test_format_chord_progression_invalid():
    from src.note_gen.models.patterns import Patterns
    COMMON_PROGRESSIONS = Patterns.COMMON_PROGRESSIONS
    progression_name = "Invalid Progression"
    roman_progression = ["X", "Y", "Z"]  # Invalid Roman numerals

    with pytest.raises(ValueError):
        await format_chord_progression(progression_name, roman_progression)


@pytest.mark.asyncio
async def test_format_chord_progression_empty():
    from src.note_gen.models.patterns import Patterns
    COMMON_PROGRESSIONS = Patterns.COMMON_PROGRESSIONS
    progression_name = "Empty Progression"
    roman_progression = []  # Empty input

    with pytest.raises(ValueError):
        await format_chord_progression(progression_name, roman_progression)
