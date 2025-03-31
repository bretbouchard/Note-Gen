import unittest
from typing import Dict, Any
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.core.constants import NOTE_PATTERNS
from src.note_gen.core.enums import PatternDirection, ScaleType

class TestPresets(unittest.TestCase):
    def setUp(self):
        self.test_patterns = NOTE_PATTERNS
        self.test_pattern_name = "minor_triad"
        
    def test_pattern_structure(self):
        """Test that pattern presets have the required structure."""
        # Check if patterns exist
        self.assertIsInstance(self.test_patterns, dict)
        self.assertGreater(len(self.test_patterns), 0)
        
        # Check specific pattern
        pattern = self.test_patterns[self.test_pattern_name]
        self.assertIsInstance(pattern, dict)
        self.assertIn('intervals', pattern)
        self.assertIsInstance(pattern['intervals'], list)
        
        # Create pattern from preset
        note_pattern = NotePattern.from_preset(self.test_pattern_name)
        
        # Validate pattern structure
        self.assertIsInstance(note_pattern, NotePattern)
        self.assertEqual(note_pattern.name, self.test_pattern_name)
        self.assertIsInstance(note_pattern.data, NotePatternData)
        self.assertEqual(note_pattern.data.intervals, pattern['intervals'])
        
        # Validate initial note
        self.assertGreaterEqual(len(note_pattern.pattern), 1)
        self.assertEqual(note_pattern.pattern[0].pitch, 'C')  # Check pitch instead of note_name
        self.assertEqual(note_pattern.pattern[0].octave, 4)   # Check octave separately

    def test_pattern_creation(self):
        """Test creating patterns from presets."""
        pattern = NotePattern.from_preset(self.test_pattern_name)
        self.assertIsInstance(pattern, NotePattern)
        self.assertIsInstance(pattern.data, NotePatternData)
        self.assertEqual(pattern.name, self.test_pattern_name)
        self.assertGreaterEqual(len(pattern.pattern), 1)

    def test_invalid_preset(self):
        """Test handling of invalid preset names."""
        with self.assertRaises(ValueError):
            NotePattern.from_preset("nonexistent_pattern")
