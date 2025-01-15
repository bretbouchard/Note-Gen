import pytest
from note_gen.fetch_patterns import (
    fetch_chord_progressions,
    fetch_note_patterns,
    fetch_rhythm_patterns,
    fetch_chord_progression_by_id,
    fetch_note_pattern_by_id,
    fetch_rhythm_pattern_by_id,
)
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.note_pattern import NotePattern
from note_gen.models.rhythm_pattern import RhythmPattern
from note_gen.models.rhythm_pattern import RhythmPatternData
from pymongo.database import Database
from typing import Any

class TestFetchPatterns:
    def test_fetch_chord_progressions(self, mock_db: Database[Any]):
        # Using mock database
        result = fetch_chord_progressions(mock_db)
        assert len(result) > 0
        assert isinstance(result[0], ChordProgression)
        assert isinstance(result[0].id, str)

    def test_fetch_note_patterns(self, mock_db: Database[Any]):
        # Using mock database
        result = fetch_note_patterns(mock_db)
        assert len(result) > 0
        assert isinstance(result[0], NotePattern)
        assert isinstance(result[0].id, str)

    def test_fetch_rhythm_patterns(self, mock_db: Database[Any]):
        # Using mock database
        result = fetch_rhythm_patterns(mock_db)
        assert len(result) > 0
        assert isinstance(result[0], RhythmPattern)
        assert isinstance(result[0].id, str)

    def test_fetch_chord_progression_by_id(self, mock_db: Database[Any]):
        # Get first chord progression's ID
        progressions = fetch_chord_progressions(mock_db)
        assert len(progressions) > 0
        test_id = progressions[0].id
        
        # Using mock database
        result = fetch_chord_progression_by_id(test_id, mock_db)
        assert isinstance(result, ChordProgression)
        assert result.id == test_id

    def test_fetch_note_pattern_by_id(self, mock_db: Database[Any]):
        # Get first note pattern's ID
        patterns = fetch_note_patterns(mock_db)
        assert len(patterns) > 0
        test_id = patterns[0].id
        
        # Using mock database
        result = fetch_note_pattern_by_id(test_id, mock_db)
        assert isinstance(result, NotePattern)
        assert result.id == test_id

    def test_fetch_rhythm_pattern_by_id(self, mock_db: Database[Any]):
        # Get first rhythm pattern's ID
        patterns = fetch_rhythm_patterns(mock_db)
        assert len(patterns) > 0
        test_id = patterns[0].id
        
        # Using mock database
        result = fetch_rhythm_pattern_by_id(test_id, mock_db)
        assert isinstance(result, RhythmPattern)
        assert result.id == test_id

    def test_fetch_chord_progression_by_id_not_found(self, mock_db: Database[Any]):
        result = fetch_chord_progression_by_id("nonexistent-id", mock_db)
        assert result is None

    def test_fetch_note_pattern_by_id_not_found(self, mock_db: Database[Any]):
        result = fetch_note_pattern_by_id("nonexistent-id", mock_db)
        assert result is None

    def test_fetch_rhythm_pattern_by_id_not_found(self, mock_db: Database[Any]):
        result = fetch_rhythm_pattern_by_id("nonexistent-id", mock_db)
        assert result is None
