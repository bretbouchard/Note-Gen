import pytest
from typing import List, Dict
from src.note_gen.factories.chord_progression_factory import ChordProgressionFactory
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.core.enums import ScaleType, ChordQuality, ValidationLevel

@pytest.fixture
def scale_info():
    return ScaleInfo(
        key="C",
        scale_type=ScaleType.MAJOR,
        tonic="C4"
    )

@pytest.fixture
def factory(scale_info):
    return ChordProgressionFactory(
        scale_info=scale_info,
        validation_level=ValidationLevel.NORMAL
    )

class TestChordProgressionFactory:
    async def test_from_preset(self, factory):
        progression = await ChordProgressionFactory.from_preset(
            preset_name="basic",
            root_note="C",
            scale_type=ScaleType.MAJOR
        )
        assert isinstance(progression, ChordProgression)
        assert progression.root_note == "C"
        assert progression.name == "basic"

    async def test_from_pattern(self, factory):
        pattern = [
            (1, ChordQuality.MAJOR),
            (4, ChordQuality.MAJOR),
            (5, ChordQuality.MAJOR)
        ]
        progression = await ChordProgressionFactory.from_pattern(
            pattern=pattern,
            root_note="C",
            scale_type=ScaleType.MAJOR
        )
        assert len(progression.chords) == 3
        assert progression.chords[0].root == "C"

    async def test_from_genre(self, factory):
        progression = await ChordProgressionFactory.from_genre(
            genre="pop",
            root_note="C",
            scale_type=ScaleType.MAJOR
        )
        assert isinstance(progression, ChordProgression)
        assert len(progression.chords) >= 4

    async def test_custom(self, factory):
        chord_data = [
            {"root": "C", "quality": ChordQuality.MAJOR},
            {"root": "F", "quality": ChordQuality.MAJOR},
            {"root": "G", "quality": ChordQuality.MAJOR}
        ]
        progression = await ChordProgressionFactory.custom(
            chord_data=chord_data,
            root_note="C",
            scale_type=ScaleType.MAJOR
        )
        assert len(progression.chords) == 3
        assert progression.metadata["source"] == "custom"

    async def test_invalid_preset(self, factory):
        with pytest.raises(ValueError):
            await ChordProgressionFactory.from_preset(
                preset_name="nonexistent",
                root_note="C",
                scale_type=ScaleType.MAJOR
            )

    async def test_invalid_genre(self, factory):
        with pytest.raises(ValueError):
            await ChordProgressionFactory.from_genre(
                genre="invalid_genre",
                root_note="C",
                scale_type=ScaleType.MAJOR
            )