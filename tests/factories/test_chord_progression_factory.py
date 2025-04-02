import pytest
from src.note_gen.factories.chord_progression_factory import ChordProgressionFactory
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.core.enums import ScaleType, ChordQuality

class TestChordProgressionFactory:
    @pytest.mark.asyncio
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
        
        # Test the actual chord progression
        expected_roots = ["C", "G", "A", "F"]  # The roots of I-V-vi-IV in C major
        actual_roots = [item.chord.root for item in progression.items]
        assert actual_roots == expected_roots

    @pytest.mark.asyncio
    async def test_from_pattern(self):
        """Test creating progression from pattern."""
        pattern = [(1, "MAJOR"), (4, "MAJOR"), (5, "MAJOR")]
        progression = await ChordProgressionFactory.from_pattern(
            pattern=pattern,
            key="C",
            scale_type=ScaleType.MAJOR,
            time_signature=(4, 4)  # Add time_signature
        )
        
        assert isinstance(progression, ChordProgression)
        assert progression.key == "C"
        assert len(progression.items) == 3
        assert progression.time_signature == (4, 4)
        
        # Test the actual chord progression
        expected_roots = ["C", "F", "G"]  # The roots of I-IV-V in C major
        actual_roots = [item.chord.root for item in progression.items]
        assert actual_roots == expected_roots

    @pytest.mark.asyncio
    async def test_from_genre(self):
        """Test creating progression from genre."""
        progression = await ChordProgressionFactory.from_genre(
            genre="rock",
            key="C",
            scale_type=ScaleType.MAJOR,
            length=4,
            time_signature=(4, 4)  # Add time_signature
        )
        
        assert isinstance(progression, ChordProgression)
        assert progression.key == "C"
        assert len(progression.items) == 4
        assert progression.time_signature == (4, 4)
        
        # Test the first rock pattern (I-IV-V-V)
        expected_roots = ["C", "F", "G", "G"]
        actual_roots = [item.chord.root for item in progression.items]
        assert actual_roots == expected_roots
