import unittest
import logging
from typing import List, Optional
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.enums import ScaleType
from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class TestChordProgression(unittest.TestCase):
    def test_create_chord_progression_valid_data(self) -> None:
        """Test creating a chord progression with valid data."""
        logger.debug("Starting test_create_chord_progression_valid_data")
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR),
        ]
        logger.debug(f"Chords created: {chords}")

        scale_info = ScaleInfo(
            root=Note(note_name='C', octave=4, duration=1.0, velocity=100),
            key='C',
            scale_type=ScaleType.MINOR
        )

        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type=ScaleType.MINOR.value,
            scale_info=scale_info,
            complexity=0.7
        )

        assert progression.name == "Test Progression"
        assert len(progression.chords) == 3
        assert progression.key == "C" 
        assert progression.scale_type == ScaleType.MINOR.value
        assert progression.complexity == 0.7

    def test_chord_progression_scale_types(self) -> None:
        """Test chord progression with different scale types."""
        test_cases = [
            (ScaleType.MAJOR, "C", ["C", "F", "G"]),
            (ScaleType.MINOR, "Am", ["A", "D", "E"])
        ]

        for scale_type, key, chord_roots in test_cases:
            root_note = key[0]  # Get the root note without any modifiers
            chords = [
                Chord(
                    root=Note(note_name=root, octave=4, duration=1.0, velocity=100),
                    quality=ChordQuality.MAJOR if scale_type == ScaleType.MAJOR else ChordQuality.MINOR
                ) 
                for root in chord_roots
            ]
            
            progression = ChordProgression(
                name="Test Progression",
                chords=chords,
                key=key,
                scale_type=scale_type.value,
                scale_info=ScaleInfo(
                    root=Note(note_name=root_note, octave=4, duration=1.0, velocity=100),
                    key=key,
                    scale_type=scale_type
                ),
                complexity=0.7
            )
            
            assert progression.key == key
            assert progression.scale_type == scale_type.value

    def test_chord_progression_validation(self) -> None:
        """Test chord progression validation rules."""
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Invalid Scale Type",
                chords=[
                    Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR)
                ],
                key="C",
                scale_type="INVALID_SCALE",  # Invalid scale type
                scale_info=ScaleInfo(
                    root=Note(note_name="C", octave=4),
                    key="C",
                    scale_type=ScaleType.MAJOR
                ),
                complexity=0.5
            )

    def test_chord_progression_mismatched_scale_info(self) -> None:
        """Test chord progression with mismatched scale info."""
        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Mismatched Scale Info",
                chords=[
                    Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR)
                ],
                key="C",
                scale_type=ScaleType.MAJOR.value,
                scale_info=ScaleInfo(  # Mismatched key and scale type
                    root=Note(note_name="D", octave=4),
                    key="D",
                    scale_type=ScaleType.MINOR
                ),
                complexity=0.5
            )

    def test_chord_progression_optional_fields(self) -> None:
        """Test optional fields in chord progression."""
        progression = ChordProgression(
            name="Test Optional Fields",
            chords=[
                Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR),
            ],
            key="C",
            scale_type=ScaleType.MAJOR.value,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.5,
            genre="jazz",
            id="test-id"
        )
        assert progression.genre == "jazz"
        assert progression.id == "test-id"

        progression_no_id = ChordProgression(
            name="Test No ID",
            chords=[
                Chord(root=Note(note_name="C", octave=4), quality=ChordQuality.MAJOR),
            ],
            key="C",
            scale_type=ScaleType.MAJOR.value,
            scale_info=ScaleInfo(
                root=Note(note_name='C', octave=4),
                key='C',
                scale_type=ScaleType.MAJOR
            ),
            complexity=0.5
        )
        assert progression_no_id.id is None

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
        # Create a list of 33 chords (exceeding max_items=32)
        too_many_chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)
        ] * 33

        with self.assertRaises(ValidationError):
            ChordProgression(
                name="Invalid Progression",
                chords=too_many_chords,
                key="C",
                scale_type=ScaleType.MAJOR,
                scale_info=ScaleInfo(
                    key='C',
                    scale_type=ScaleType.MAJOR
                ),
                complexity=0.6
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
        # Test valid keys
        valid_keys = [
            ("C", ScaleType.MAJOR), 
            ("F#", ScaleType.MAJOR),
            ("Bb", ScaleType.MAJOR),
            ("Am", ScaleType.MINOR),
            ("Em", ScaleType.MINOR),
            ("G#m", ScaleType.MINOR)
        ]
        
        for key, scale_type in valid_keys:
            root_note = key[0] if '#' not in key else key[:2]
            ChordProgression(
                name="Valid Progression",
                chords=[
                    Chord(
                        root=Note(note_name=root_note, octave=4, duration=1.0, velocity=100),
                        quality=ChordQuality.MAJOR if scale_type == ScaleType.MAJOR else ChordQuality.MINOR
                    )
                ],
                key=key,
                scale_type=scale_type.value,
                scale_info=ScaleInfo(
                    root=Note(note_name=root_note, octave=4, duration=1.0, velocity=100),
                    key=key,
                    scale_type=scale_type
                ),
                complexity=0.4
            )

        # Test invalid keys
        invalid_keys = ["H", "Cm7", "Bb+", "x", "123"]
        for key in invalid_keys:
            with self.assertRaises(ValidationError):
                ChordProgression(
                    name="Invalid Progression",
                    chords=[Chord(root=Note(note_name="C", octave=4))],
                    key=key,
                    scale_type=ScaleType.MAJOR.value,
                    scale_info=ScaleInfo(root=Note(note_name="C", octave=4)),
                    complexity=0.4
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
        from src.note_gen.models.patterns import ChordProgression, NotePattern, NotePatternData
        from src.note_gen.models.scale import Scale
        from src.note_gen.models.enums import ScaleType
        from src.note_gen.models.scale_info import ScaleInfo
        from src.note_gen.models.note import Note
        from src.note_gen.models.chord import Chord, ChordQuality
        
        # Create test notes
        c_note = Note(note_name='C', octave=4, duration=1.0, velocity=100)
        e_note = Note(note_name='E', octave=4, duration=1.0, velocity=100)
        g_note = Note(note_name='G', octave=4, duration=1.0, velocity=100)
        
        # Create a note pattern with valid data
        note_pattern = NotePattern(
            name="Test Pattern",
            intervals=[0, 4, 7],  # C major triad intervals
            description="A test pattern for progression generation",
            tags=['test_pattern'],
            complexity=0.5,
            data=NotePatternData(
                intervals=[0, 4, 7],  # C major triad intervals
                notes=[c_note, e_note, g_note]  # C major triad notes
            )
        )
    
        scale_info = ScaleInfo(
            root=c_note,
            key='C',
            scale_type=ScaleType.MAJOR
        )
    
        # Create initial chords for the progression
        initial_chords = [
            Chord(root=c_note, quality=ChordQuality.MAJOR),
            Chord(root=g_note, quality=ChordQuality.MAJOR)
        ]
    
        # Create an instance of ChordProgression
        chord_progression = ChordProgression(
            name="Test Progression",
            chords=initial_chords,
            key="C",
            scale_type=ScaleType.MAJOR.value,  # Use the string value
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
        self.assertEqual(progression.scale_type, ScaleType.MAJOR.value)  # Compare with string value

if __name__ == "__main__":
    unittest.main()