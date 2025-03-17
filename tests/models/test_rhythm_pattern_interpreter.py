import pytest
from unittest.mock import AsyncMock
from src.note_gen.models.patterns import RhythmPatternData, RhythmNote, NotePattern
from src.note_gen.models.pattern_interpreter import ScalePatternInterpreter
from src.note_gen.models.note import Note

@pytest.fixture
def mock_db_connection() -> AsyncMock:
    return AsyncMock()

class FakeScale:
    def get_notes(self):
        return [Note(note_name="C", octave=4)]

class TestRhythmPatternInterpreter:
    async def test_pattern_interpreter_get_next_note(self, mock_db_connection: AsyncMock) -> None:
        scale = FakeScale()
        pattern = [Note(note_name="C", octave=4)]
        interpreter = ScalePatternInterpreter(scale=scale, pattern=pattern)
        
        first_note = interpreter.get_next_note()
        second_note = interpreter.get_next_note()

        assert str(first_note) == "C4"
        assert str(second_note) == "C4"  # Should cycle back

    async def test_generate_note_sequence(self, mock_db_connection: AsyncMock) -> None:
        scale = FakeScale()
        rhythm_notes = [RhythmNote(position=0, duration=1)]
        rhythm_pattern = RhythmPatternData(
            name="Test Pattern",
            notes=rhythm_notes,
            time_signature="4/4",
            default_duration=1.0,
            style="rock",
            groove_type="straight",
            pattern="4 4 4 4"
        )
        note_pattern = NotePattern(
            name="Test Note Pattern",
            notes=[Note(note_name="C", octave=4)],
            pattern_type="scale",
            description="Test pattern",
            tags=["test"],
            complexity=1.0,
            data=[0]
        )
        
        sequence = await ScalePatternInterpreter.generate_note_sequence(
            scale=scale,
            chord_progression=None,
            note_pattern=note_pattern,
            rhythm_pattern=rhythm_pattern
        )
        
        assert len(sequence.notes) == 1
        assert sequence.notes[0].note_name == "C"
        assert sequence.notes[0].octave == 4
