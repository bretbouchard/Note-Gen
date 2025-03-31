import pytest
from src.note_gen.factories.pattern_factory import PatternFactory
from src.note_gen.models.patterns import NotePattern, RhythmPattern, RhythmNote
from src.note_gen.core.enums import ScaleType

class TestPatternFactory:
    @pytest.fixture
    def factory(self):
        return PatternFactory()

    def test_create_rhythm_pattern(self, factory):
        """Test creating a rhythm pattern."""
        durations = [1.0, 0.5, 0.5]
        pattern = factory.create_rhythm_pattern(
            durations=durations,
            time_signature=(4, 4)
        )

        assert isinstance(pattern, RhythmPattern)
        assert len(pattern.pattern) == 3
        assert sum(note.duration for note in pattern.pattern) == 2.0
        assert pattern.time_signature == (4, 4)
        assert all(isinstance(note, RhythmNote) for note in pattern.pattern)
