import pytest
from src.note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_note_patterns,
    fetch_rhythm_patterns,
    fetch_chord_progression_by_id,
    fetch_note_pattern_by_id,
    fetch_rhythm_pattern_by_id,
)
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import RhythmPattern
from src.note_gen.models.rhythm_pattern import RhythmPatternData


class TestFetchPatterns:
    def test_fetch_chord_progressions(self):
        # Using real data from the database
        result = fetch_chord_progressions()  # Pull real data
        assert len(result) > 0  # Ensure we have results
        assert isinstance(result[0], ChordProgression)
        assert result[0].id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    def test_fetch_note_patterns(self):
        # Using real data from the database
        result = fetch_note_patterns()  # Pull real data
        assert len(result) > 0  # Ensure we have results
        assert isinstance(result[0], NotePattern)
        assert result[0].id in [1, 2, 3, 4, 5]

    def test_fetch_rhythm_patterns(self):
        # Using real data from the database
        result = fetch_rhythm_patterns()  # Pull real data
        assert len(result) > 0  # Ensure we have results
        assert isinstance(result[0], RhythmPattern)
        assert result[0].id in [1, 2, 3, 4]

    def test_fetch_chord_progression_by_id(self):
        # Using real data from the database
        result = fetch_chord_progression_by_id(1)  # Pull real data by ID
        assert isinstance(result, ChordProgression)

    def test_fetch_note_pattern_by_id(self):
        # Using real data from the database
        result = fetch_note_pattern_by_id(1)  # Pull real data by ID
        assert isinstance(result, NotePattern)

    def test_fetch_rhythm_pattern_by_id(self):
        # Using real data from the database
        result = fetch_rhythm_pattern_by_id(1)  # Pull real data by ID
        assert isinstance(result, RhythmPattern)

    def test_fetch_chord_progression_by_id_not_found(self):
        result = fetch_chord_progression_by_id(99)
        assert result is None

    def test_fetch_note_pattern_by_id_not_found(self):
        result = fetch_note_pattern_by_id(99)
        assert result is None

    def test_fetch_rhythm_pattern_by_id_not_found(self):
        result = fetch_rhythm_pattern_by_id(99)
        assert result is None
