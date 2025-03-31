import unittest
from unittest.mock import AsyncMock, patch
from src.note_gen.api.pattern_api import (
    fetch_chord_progressions,
    fetch_note_patterns,
    fetch_rhythm_patterns,
    fetch_chord_progression_by_id,
    fetch_note_pattern_by_id,
    fetch_rhythm_pattern_by_id
)
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.models.rhythm import RhythmPattern, RhythmNote
from src.note_gen.core.enums import PatternDirection, ScaleType
from motor.motor_asyncio import AsyncIOMotorDatabase
import pytest

class TestPatternFetching(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db_mock = AsyncMock(spec=AsyncIOMotorDatabase)
        
        # Sample test data
        self.test_note_pattern = NotePattern(
            name="test_pattern",
            pattern=[],  # This should be a list of Note objects
            data=NotePatternData(
                intervals=[0, 2, 4],
                direction=PatternDirection.UP,
                scale_type=ScaleType.MAJOR
            ),
            time_signature=(4, 4)
        )
        
        self.test_rhythm_pattern = RhythmPattern(
            name="test_rhythm",
            pattern=[  # Changed from durations to pattern with RhythmNote objects
                RhythmNote(position=0.0, duration=1.0),
                RhythmNote(position=1.0, duration=0.5),
                RhythmNote(position=1.5, duration=0.5)
            ],
            time_signature=(4, 4),  # Fixed: Changed from string "4/4" to tuple (4, 4)
            description="Test rhythm pattern"
        )

    @patch('src.note_gen.api.pattern_api.get_database')
    async def test_fetch_note_patterns(self, mock_get_db):
        mock_get_db.return_value = self.db_mock
        self.db_mock.note_patterns.find.return_value = [
            self.test_note_pattern.model_dump()
        ]
        
        patterns = await fetch_note_patterns()
        self.assertIsInstance(patterns, list)
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].name, "test_pattern")

    @patch('src.note_gen.api.pattern_api.get_database')
    async def test_fetch_rhythm_patterns(self, mock_get_db):
        mock_get_db.return_value = self.db_mock
        self.db_mock.rhythm_patterns.find.return_value = [
            self.test_rhythm_pattern.model_dump()
        ]
        
        patterns = await fetch_rhythm_patterns()
        self.assertIsInstance(patterns, list)
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].name, "test_rhythm")

    @patch('src.note_gen.api.pattern_api.get_database')
    async def test_fetch_pattern_by_id(self, mock_get_db):
        mock_get_db.return_value = self.db_mock
        test_id = "test123"
        
        self.db_mock.note_patterns.find_one.return_value = (
            self.test_note_pattern.model_dump()
        )
        
        pattern = await fetch_note_pattern_by_id(test_id)
        self.assertIsInstance(pattern, NotePattern)
        self.assertEqual(pattern.name, "test_pattern")

    @patch('src.note_gen.api.pattern_api.get_database')
    async def test_fetch_nonexistent_pattern(self, mock_get_db):
        mock_get_db.return_value = self.db_mock
        self.db_mock.note_patterns.find_one.return_value = None
        
        with self.assertRaises(ValueError):
            await fetch_note_pattern_by_id("nonexistent")

    @patch('src.note_gen.api.pattern_api.get_database')
    async def test_database_error(self, mock_get_db):
        mock_get_db.return_value = self.db_mock
        self.db_mock.note_patterns.find.side_effect = Exception("Database error")
        
        with self.assertRaises(Exception):
            await fetch_note_patterns()

if __name__ == '__main__':
    unittest.main()
