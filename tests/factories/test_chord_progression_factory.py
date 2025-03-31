import pytest
from src.note_gen.factories.chord_progression_factory import ChordProgressionFactory
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.core.enums import ScaleType, ChordQuality

class TestChordProgressionFactory:
    async def test_from_preset(self):
        """Test creating progression from preset."""
        progression = await ChordProgressionFactory.from_preset(
            preset_name="pop",
            key="C",
            scale_type=ScaleType.MAJOR,
            time_signature=(4, 4)
        )
        
        assert isinstance(progression, ChordProgression)
        assert progression.key == "C"
        assert len(progression.items) == 4
        assert progression.time_signature == (4, 4)

    async def test_from_pattern(self):
        """Test creating progression from pattern."""
        pattern = [(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR)]
        progression = await ChordProgressionFactory.from_pattern(
            pattern=pattern,
            key="C",
            scale_type=ScaleType.MAJOR,
            name="Test Pattern"
        )
        
        assert isinstance(progression, ChordProgression)
        assert progression.key == "C"
        assert len(progression.items) == 2
        assert progression.name == "Test Pattern"

    async def test_from_genre(self):
        """Test creating progression from genre."""
        progression = await ChordProgressionFactory.from_genre(
            genre="pop",
            key="C",
            scale_type=ScaleType.MAJOR
        )
        
        assert isinstance(progression, ChordProgression)
        assert progression.key == "C"
        assert len(progression.items) == 4
        assert "Pop" in progression.name
