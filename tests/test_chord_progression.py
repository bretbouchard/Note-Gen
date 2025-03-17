import pytest
from src.note_gen.models.patterns import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord


def test_chord_progression_with_string_scale_info() -> None:
    progression = ChordProgression(
        name='Test Progression',
        key='C',
        scale_type='MAJOR',
        scale_info='C',
        chords=[Chord(root='C', quality='MAJOR'), Chord(root='G', quality='MAJOR')]
    )
    assert progression.scale_info == 'C'


def test_chord_progression_with_scale_info_object() -> None:
    scale = ScaleInfo(key='C', scale_type='MAJOR')
    progression = ChordProgression(
        name='Test Progression',
        key='C',
        scale_type='MAJOR',
        scale_info=scale,
        chords=[Chord(root='C', quality='MAJOR'), Chord(root='G', quality='MAJOR')]
    )
    assert progression.scale_info == 'C'


def test_chord_progression_invalid_scale_info_string() -> None:
    with pytest.raises(ValueError, match="Invalid scale info format"):
        ChordProgression(
            name='Test Progression',
            key='C',
            scale_type='MAJOR',
            scale_info='H',  # Invalid key
            chords=[Chord(root='C', quality='MAJOR'), Chord(root='G', quality='MAJOR')]
        )


def test_chord_progression_invalid_scale_info_type() -> None:
    with pytest.raises(ValueError, match="scale_info must be either a string or ScaleInfo object"):
        ChordProgression(
            name='Test Progression',
            key='C',
            scale_type='MAJOR',
            scale_info=123,  # Invalid type
            chords=[Chord(root='C', quality='MAJOR'), Chord(root='G', quality='MAJOR')]
        )
