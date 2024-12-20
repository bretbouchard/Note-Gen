import pytest
from src.models.note_pattern import NotePattern, NotePatternData
from src.models.note import Note


def test_note_pattern_creation() -> None:
    """Test creation of NotePattern with valid data."""
    notes: list[Note] = [Note(name='C', pitch='C4', duration=1.0, velocity=64)]  # Use valid note name
    note_pattern_data: NotePatternData = NotePatternData(notes=notes)
    note_pattern: NotePattern = NotePattern(name='ValidPattern', data=note_pattern_data)
    assert note_pattern.name == 'ValidPattern'
    if isinstance(note_pattern.data, NotePatternData):
        assert len(note_pattern.data.notes) == 1


def test_invalid_note_pattern() -> None:
    """Test handling of invalid note pattern data."""
    with pytest.raises(ValueError):
        NotePattern(name='', data=NotePatternData(notes=[]))


def test_note_pattern_total_duration() -> None:
    """Test the assignment of notes in the pattern."""
    notes: list[Note] = [Note(name='C', pitch='C4', duration=1.0, velocity=64),
                         Note(name='D', pitch='D4', duration=2.0, velocity=64)]
    note_pattern_data: NotePatternData = NotePatternData(notes=notes)
    note_pattern: NotePattern = NotePattern(name='MyPattern', data=note_pattern_data)
    
    # Assert that the notes are assigned correctly by checking MIDI numbers
    if isinstance(note_pattern.data, NotePatternData):
        assert len(note_pattern.data.notes) == 2
        assert isinstance(note_pattern.data.notes[0], Note)
        if isinstance(note_pattern.data.notes[0], Note):
            assert note_pattern.data.notes[0].midi_number == 60  # C4 MIDI number
        assert isinstance(note_pattern.data.notes[1], Note)
        if isinstance(note_pattern.data.notes[1], Note):
            assert note_pattern.data.notes[1].midi_number == 62  # D4 MIDI number


def test_invalid_note_data() -> None:
    """Test handling of invalid note data."""
    with pytest.raises(ValueError):
        Note(pitch='', duration=-1.0, velocity=200)


def test_empty_notes() -> None:
    """Test handling of empty notes in NotePatternData."""
    with pytest.raises(ValueError):
        NotePatternData(notes=[])


def test_invalid_note_type() -> None:
    """Test handling of invalid note types."""
    with pytest.raises(ValueError):
        NotePatternData(notes=[None])
