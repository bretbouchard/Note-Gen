import pytest
from pydantic import ConfigDict, ValidationError
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.core.enums import ScaleType, ChordQuality


def test_chord_progression_with_string_scale_info() -> None:
    progression = ChordProgression(
        name='Test Progression',
        key='C',
        scale_type=ScaleType.MAJOR,
        scale_info='C',
        chords=[Chord(root='C', quality=ChordQuality.MAJOR, inversion=0), 
                Chord(root='G', quality=ChordQuality.MAJOR, inversion=0)],
        description=None,
        tags=None,
        complexity=0.0,
        quality=None
    )
    assert progression.scale_info == 'C'


def test_chord_progression_with_scale_info_object() -> None:
    # Create the scale_info with the root parameter
    scale = ScaleInfo(root='C', key='C', scale_type=ScaleType.MAJOR)
    progression = ChordProgression(
        name='Test Progression',
        key='C',
        scale_type=ScaleType.MAJOR,
        scale_info=scale,
        chords=[Chord(root='C', quality=ChordQuality.MAJOR, inversion=0), 
                Chord(root='G', quality=ChordQuality.MAJOR, inversion=0)],
        description=None,
        tags=None,
        complexity=0.0,
        quality=None
    )
    assert isinstance(progression.scale_info, ScaleInfo)


def test_chord_progression_invalid_scale_info_string() -> None:
    with pytest.raises(ValueError, match="Invalid scale info format"):
        ChordProgression(
            name='Test Progression',
            key='C',
            scale_type=ScaleType.MAJOR,
            scale_info='H',  # Invalid key
            chords=[Chord(root='C', quality=ChordQuality.MAJOR, inversion=0), 
                    Chord(root='G', quality=ChordQuality.MAJOR, inversion=0)],
            description=None,
            tags=None,
            complexity=0.0,
            quality=None
        )


def test_chord_progression_invalid_scale_info_type() -> None:
    with pytest.raises(ValueError, match="scale_info must be either a string or ScaleInfo object"):
        ChordProgression(
            name='Test Progression',
            key='C',
            scale_type=ScaleType.MAJOR,
            scale_info=123,  # Invalid type
            chords=[Chord(root='C', quality=ChordQuality.MAJOR, inversion=0), 
                    Chord(root='G', quality=ChordQuality.MAJOR, inversion=0)],
            description=None,
            tags=None,
            complexity=0.0,
            quality=None
        )
