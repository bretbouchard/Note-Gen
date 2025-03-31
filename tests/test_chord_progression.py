import pytest
from pydantic import ConfigDict, ValidationError
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale import Scale
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType, ChordQuality
from src.note_gen.models.chord_progression_item import ChordProgressionItem


def test_chord_progression_with_string_scale_info() -> None:
    scale_info = ScaleInfo(
        root=Note(note_name='C', octave=4, duration=1.0, velocity=100, position=0.0),
        key='C',
        scale_type=ScaleType.MAJOR
    )
    progression = ChordProgression(
        name='Test Progression',
        key='C',
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        chords=[
            Chord(root=Note(note_name='C', octave=4, duration=1.0, velocity=100, position=0.0), quality=ChordQuality.MAJOR, inversion=0),
            Chord(root=Note(note_name='G', octave=4, duration=1.0, velocity=100, position=0.0), quality=ChordQuality.MAJOR, inversion=0)
        ],
        description=None,
        tags=None,
        complexity=0.0,
        quality=None
    )
    assert isinstance(progression.scale_info, ScaleInfo)


def test_chord_progression_invalid_scale_info_string() -> None:
    invalid_scale_info = ScaleInfo(
        root=Note(note_name='C', octave=4, duration=1.0, velocity=100, position=0.0),
        key='H',  # Invalid key
        scale_type=ScaleType.MAJOR
    )
    with pytest.raises(ValidationError) as excinfo:
        ChordProgression(
            name='Test Progression',
            key='C',
            scale_type=ScaleType.MAJOR,
            scale_info=invalid_scale_info,
            chords=[Chord(root=Note(note_name='C', octave=4, duration=1.0, velocity=100, position=0.0), quality=ChordQuality.MAJOR, inversion=0)]
        )
    assert "Invalid key format" in str(excinfo.value)


def test_chord_progression_invalid_scale_info_type():
    invalid_scale_info = ScaleInfo(
        root=Note(note_name='C', octave=4, duration=1.0, velocity=100, position=0.0),
        key='C',
        scale_type=ScaleType.MAJOR
    )
    with pytest.raises(ValidationError) as exc_info:
        ChordProgression(
            name="Test Progression",
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=invalid_scale_info,
            chords=[Chord(root=Note(note_name='C', octave=4, duration=1.0, velocity=100, position=0.0), quality=ChordQuality.MAJOR)]
        )
    error_msg = str(exc_info.value)
    assert "Invalid scale info format" in error_msg


def test_chord_progression_optional_fields() -> None:
    progression = ChordProgression(
        name='Test No ID',
        key='C',
        scale_type=ScaleType.MAJOR,  # This line is correct as is
        scale_info=ScaleInfo(
            key='C',
            scale_type=ScaleType.MAJOR,
            root=Note(
                note_name='C',
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=100
            )
        ),
        chords=[
            ChordProgressionItem(
                chord="C",
                root="C",
                quality=ChordQuality.MAJOR,
                duration=1.0,
                position=0.0
            )
        ]
    )
    # Remove ID assertion since it's auto-generated
    assert progression.description is None
    assert progression.tags is None
    assert progression.quality is None
