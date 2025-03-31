import pytest
from pydantic import ValidationError
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord_progression_item import ChordProgressionItem
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType, ChordQuality


def test_chord_progression_with_string_scale_info() -> None:
    scale_info = ScaleInfo(
        root=Note(
            pitch="C",
            octave=4,
            duration=1.0,
            velocity=100,
            position=0.0
        ),
        key='C',
        scale_type=ScaleType.MAJOR
    )
    
    # Create ChordProgressionItem instances first
    items = [
        ChordProgressionItem.create("C", 1.0, 0.0),
        ChordProgressionItem.create("G", 1.0, 1.0)
    ]
    
    progression = ChordProgression(
        name='Test Progression',
        key='C',
        scale_type=ScaleType.MAJOR,
        scale_info=scale_info,
        items=items
    )
    assert isinstance(progression.scale_info, ScaleInfo)


def test_chord_progression_invalid_scale_info_type():
    # Create ChordProgressionItem instance first
    item = ChordProgressionItem.create("C", 1.0, 0.0)
    
    with pytest.raises(ValidationError) as exc_info:
        ChordProgression(
            name="Test Progression",
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info="invalid_type",  # This should raise the error
            items=[item]
        )
    assert "Input should be a valid dictionary or instance of ScaleInfo" in str(exc_info.value)


def test_chord_progression_optional_fields() -> None:
    # Create ChordProgressionItem instance first
    item = ChordProgressionItem.create("C", 1.0, 0.0)
    
    progression = ChordProgression(
        name='Test No ID',
        key='C',
        scale_type=ScaleType.MAJOR,
        scale_info=ScaleInfo(
            key='C',
            scale_type=ScaleType.MAJOR,
            root=Note(
                pitch="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=100
            )
        ),
        items=[item]
    )
    assert progression.description is None
    assert progression.tags is None
    assert progression.quality is None
