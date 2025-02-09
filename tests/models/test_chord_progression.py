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
    def test_create_chord_progression_valid_data(self) -> None:
        logger.debug("Starting test_create_chord_progression_valid_data")
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
        ]
        logger.debug(f"Chords created: {chords}")

        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type=ScaleType.MINOR,
            scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
        )
        logger.debug(f"ChordProgression created: {progression}")
        self.assertEqual(progression.name, "Test Progression")
        self.assertEqual(len(progression.chords), 3)

    def test_empty_chords(self) -> None:
        logger.debug("Starting test_empty_chords")
        with self.assertRaises(ValidationError):
            progression = ChordProgression(
                name="Empty Chords",
                chords=[],
                key="C",
                scale_type=ScaleType.MINOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            )
            logger.debug("ValidationError expected for empty chords.")

    def test_invalid_complexity(self) -> None:
        logger.debug("Starting test_invalid_complexity")
        with self.assertRaises(ValidationError):
            progression = ChordProgression(
                name="Invalid Complexity",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100)),
                ],
                key="C",
                scale_type=ScaleType.MINOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
                complexity=1.5,
            )
            logger.debug("ValidationError expected for invalid complexity.")

    def test_model_dump(self) -> None:
        logger.debug("Starting test_model_dump")
        """
        Test the model's dump functionality.

        This test case checks if the model can be converted to a dictionary correctly.
        """
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100)),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100)),
        ]
        progression = ChordProgression(
            name="Test Model Dump",
            chords=chords,
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
        )
        logger.debug(f"ChordProgression created: {progression}")
        self.assertEqual(progression.dict(), {
            'id': progression.id,
            'name': "Test Model Dump",
            'chords': chords,
            'key': "C",
            'scale_type': ScaleType.MAJOR,
            'scale_info': progression.scale_info,
            'quality': progression.quality,
            'complexity': progression.complexity,
        })

    def test_to_dict(self):
        logger.debug("Starting test_to_dict")
        """
        Test the model's conversion to a dictionary.

        This test case checks if the model can be converted to a dictionary correctly using the to_dict method.
        """
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100)),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100)),
        ]
        progression = ChordProgression(
            name="Test To Dict",
            chords=chords,
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
        )
        logger.debug(f"ChordProgression created: {progression}")
        self.assertEqual(progression.to_dict(), {
            'id': progression.id,
            'name': "Test To Dict",
            'chords': chords,
            'key': "C",
            'scale_type': ScaleType.MAJOR,
            'scale_info': progression.scale_info,
            'quality': progression.quality,
            'complexity': progression.complexity,
        })

    def test_add_chord(self) -> None:
        logger.debug("Starting test_add_chord")
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
        logger.debug(f"ChordProgression created: {progression}")
        new_chord = Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        logger.debug(f"New chord created: {new_chord}")
        progression.add_chord(new_chord)
        logger.debug(f"Chord added to progression: {progression.chords}")
        assert len(progression.chords) == 3
        assert progression.chords[-1] == new_chord
        logger.debug("Add chord test executed")

    def test_chord_progression_edge_cases(self) -> None:    
        logger.debug("Starting test_chord_progression_edge_cases")
        """
        Test edge cases for chord progression creation.

        This test case checks for edge cases such as empty chords, invalid complexity, and invalid chord qualities.
        """
        # Test empty chords
        logger.debug("Testing empty chords edge case")
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Empty Chords",
                chords=[],
                key="C",
                scale_type=ScaleType.MINOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            )
            logger.debug("ValidationError expected for empty chords.")

        # Test invalid complexity
        logger.debug("Testing invalid complexity edge case")
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100)),
        ]
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Invalid Complexity",
                chords=chords,
                key="C",
                scale_type=ScaleType.MINOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
                complexity=1.5,
            )
            logger.debug("ValidationError expected for invalid complexity.")

        # Test invalid chord qualities
        logger.debug("Testing invalid chord quality edge case")
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Invalid Chord Quality",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality="INVALID_QUALITY"),
                ],
                key="C",
                scale_type=ScaleType.MINOR,
                scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            )
            logger.debug("ValidationError expected for invalid chord quality.")

if __name__ == "__main__":
    unittest.main()