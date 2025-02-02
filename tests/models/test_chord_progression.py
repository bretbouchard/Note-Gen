import unittest
from typing import List, Optional
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType, ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.chord import Chord
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from pydantic import ValidationError
import logging

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestChordProgression(unittest.TestCase):
    def test_create_chord_progression_valid_data(self):
        """
        Test creation of a chord progression with valid data.

        This test case checks if a chord progression can be created with valid data.
        It verifies that the chords are initialized correctly.
        """
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
        ]
        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type=ScaleType.MINOR,
            scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
        )
        self.assertEqual(progression.name, "Test Progression")
        self.assertEqual(len(progression.chords), 3)

    def test_empty_chords(self):
        """
        Test creation of a chord progression with empty chords, expecting a ValueError.

        This test case checks if creating a chord progression with empty chords raises a ValueError.
        """
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Empty Progression",
                chords=[],
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            )

    def test_invalid_complexity(self):
        """
        Test creation of a chord progression with invalid complexity, expecting a ValueError.

        This test case checks if creating a chord progression with invalid complexity raises a ValueError.
        """
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
        ]
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Invalid Complexity",
                chords=chords,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
                complexity=1.5  # Invalid complexity
            )

    def test_model_dump(self):
        """
        Test the model dump functionality of the chord progression.

        This test case checks if the model dump functionality works correctly.
        """
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
        ]
        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
        )
        dump = progression.dict()
        self.assertEqual(dump['name'], "Test Progression")

    def test_to_dict(self):
        """
        Test the to_dict method of the chord progression.

        This test case checks if the to_dict method works correctly.
        """
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
        ]
        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
        )
        dict_representation = progression.to_dict()
        self.assertEqual(dict_representation['name'], "Test Progression")
        self.assertEqual(len(dict_representation['chords']), 1)

    def test_add_chord(self):
        """
        Test adding a chord to the progression.

        This test case checks if adding a chord to the progression works correctly.
        """
        progression = ChordProgression(
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
        )
        new_chord = Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        progression.add_chord(new_chord)
        assert len(progression.chords) == 3
        assert progression.chords[-1] == new_chord
        logger.debug("Add chord test executed")

    def test_chord_progression_edge_cases(self):
        """
        Test edge cases for chord progression creation.

        This test case checks for edge cases such as empty chords, invalid complexity, and invalid chord qualities.
        """
        # Test empty chords
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Empty Progression",
                chords=[],
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            )
            logger.debug("Empty chords edge case test executed")

        # Test invalid complexity
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
        ]
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Invalid Complexity",
                chords=chords,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
                complexity=1.5  # Invalid complexity
            )
            logger.debug("Invalid complexity edge case test executed")

        # Test invalid chord qualities
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Invalid Chord Quality",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality="INVALID_QUALITY"),
                ],
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            )
            logger.debug("Invalid chord quality edge case test executed")

if __name__ == "__main__":
    unittest.main()