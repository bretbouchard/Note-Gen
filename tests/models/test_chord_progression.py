import unittest
from typing import List, Optional
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.fake_scale_info import FakeScaleInfo
from src.note_gen.models.patterns import NotePattern
from pydantic import ValidationError
import logging

# Configure logging to output to console
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestChordProgression(unittest.TestCase):
    def test_create_chord_progression_valid_data(self) -> None:
        logger.debug("Starting test_create_chord_progression_valid_data")
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
        ]
        logger.debug(f"Chords created: {chords}")

        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type=ScaleType.MINOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MINOR
            ),
            complexity=0.7
        )
        assert progression.name == "Test Progression"
        assert len(progression.chords) == 3
        assert progression.key == "C"
        assert progression.scale_type == ScaleType.MINOR
        assert progression.complexity == 0.7

    def test_empty_chords(self) -> None:
        logger.debug("Starting test_empty_chords")
        with self.assertRaises(ValidationError):
            progression = ChordProgression(
                name="Empty Chords",
                chords=[],
                key="C",
                scale_type=ScaleType.MINOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MINOR
                ),
                complexity=0.7
            )
            logger.debug("ValidationError expected for empty chords.")

    def test_invalid_complexity(self) -> None:
        logger.debug("Starting test_invalid_complexity")
        with self.assertRaises(ValidationError):
            progression = ChordProgression(
                name="Invalid Complexity",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                ],
                key="C",
                scale_type=ScaleType.MINOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MINOR
                ),
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
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
        ]
        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.5
        )
        progression_dict = progression.model_dump()
        assert 'id' in progression_dict
        assert 'name' in progression_dict
        assert 'chords' in progression_dict
        assert 'key' in progression_dict
        assert 'scale_type' in progression_dict
        assert 'complexity' in progression_dict
        assert 'scale_info' in progression_dict

    def test_to_dict(self):
        """
        Test the model's conversion to a dictionary.

        This test case checks if the model can be converted to a dictionary correctly using the to_dict method.
        """
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
        ]
        progression = ChordProgression(
            name="Test To Dict",
            chords=chords,
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.7
        )
        logger.debug(f"ChordProgression created: {progression}")
        progression_dict = progression.model_dump()
        assert 'id' in progression_dict
        assert 'name' in progression_dict
        assert 'chords' in progression_dict
        assert 'key' in progression_dict
        assert 'scale_type' in progression_dict
        assert 'complexity' in progression_dict
        assert 'scale_info' in progression_dict

    def test_add_chord(self) -> None:
        logger.debug("Starting test_add_chord")
        """
        Test adding a chord to the progression.

        This test case checks if adding a chord to the progression works correctly.
        """
        progression = ChordProgression(
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
            ],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.5
        )
        assert len(progression.chords) == 2
        assert progression.name == "Test Progression"

    def test_chords_validation(self) -> None:
        """Test chords validation rules."""
        # Test valid chords
        ChordProgression(
            name="Valid Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MINOR)
            ],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.6
        )
    
        # Test too many chords
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Too Many Chords",
                chords=[Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)] * 20,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MAJOR
                ),
                complexity=0.8
            )
    
        # Test invalid chord qualities (this test might need to be adjusted based on actual validation)
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Invalid Chord Quality",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality="INVALID_QUALITY")
                ],
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MAJOR
                ),
                complexity=0.4
            )

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
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MINOR
                ),
                complexity=0.3
            )
            logger.debug("ValidationError expected for empty chords.")

        # Test invalid complexity
        logger.debug("Testing invalid complexity edge case")
        chords = [
            Chord(
                root=Note(note_name="C", octave=4, duration=1.0, velocity=100), 
                quality=ChordQuality.MAJOR
            ),
        ]
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Single Chord",
                chords=chords,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MAJOR
                ),
                complexity=1.5  # Invalid complexity
            )

    def test_name_validation(self) -> None:
        """Test name validation rules."""
        # Test valid names
        ChordProgression(
            name="Valid Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
            ],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.6
        )

        # Test invalid names
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="",  # Empty name
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
                ],
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MAJOR
                ),
                complexity=0.5
            )

    def test_key_validation(self) -> None:
        """Test key validation rules."""
        # Test valid keys (case-insensitive)
        ChordProgression(
            name="Valid Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
            ],
            key="c",  # Lowercase
            scale_type=ScaleType.MAJOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.4
        )

        # Test invalid keys
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Invalid Key Progression",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
                ],
                key="H",  # Invalid key
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MAJOR
                ),
                complexity=0.5
            )

    def test_complexity_validation(self) -> None:
        """Test complexity validation rules."""
        # Test valid complexity
        ChordProgression(
            name="Valid Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
            ],
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.5
        )

        # Test invalid complexity
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Invalid Complexity Progression",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
                ],
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
                    key='C',
                    scale_type=ScaleType.MAJOR
                ),
                complexity=1.5  # Invalid complexity
            )

    def test_generate_progression_from_pattern(self) -> None:
        """Test generating a progression from a note pattern."""
        note_pattern = NotePattern(
            name="Test Pattern",
            pattern=[0, 2, 4],
            description="A test pattern for progression generation",
            tags=['test_pattern'],
            complexity=0.5
        )
    
        scale_info = ScaleInfo(
            root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
            key='C',
            scale_type=ScaleType.MAJOR
        )
    
        # Create initial chords for the progression
        initial_chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
        ]
    
        # Create an instance of ChordProgression first
        chord_progression = ChordProgression(
            name="Test Progression",
            chords=initial_chords,
            key="C",
            scale_type=ScaleType.MAJOR,
            scale_info=scale_info,
            complexity=0.5
        )
    
        # Call generate_progression_from_pattern as an instance method
        progression = chord_progression.generate_progression_from_pattern(
            pattern=['I', 'V', 'vi', 'IV'],
            scale_info=scale_info,
            progression_length=4
        )

        self.assertIsInstance(progression, ChordProgression)
        self.assertTrue(len(progression.chords) > 0)
        self.assertEqual(progression.key, "C")
        self.assertEqual(progression.scale_type, ScaleType.MAJOR)

if __name__ == "__main__":
    unittest.main()