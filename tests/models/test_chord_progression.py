import unittest
from typing import List
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Note, Chord
from pydantic import ValidationError
import logging

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FakeScaleInfo(ScaleInfo):
    """A fake ScaleInfo that returns placeholder notes for scale degrees."""

    def get_scale_degree_note(self, degree: int) -> Note:
        # Just map 1->C, 2->D, etc. If out of range, raise ValueError.
        note_map = {
            1: Note(note_name="C", octave=4, duration=1.0, velocity=100),
            2: Note(note_name="D", octave=4, duration=1.0, velocity=100),
            3: Note(note_name="E", octave=4, duration=1.0, velocity=100),
            4: Note(note_name="F", octave=4, duration=1.0, velocity=100),
            5: Note(note_name="G", octave=4, duration=1.0, velocity=100),
            6: Note(note_name="A", octave=4, duration=1.0, velocity=100),
            7: Note(note_name="B", octave=4, duration=1.0, velocity=100),
        }
        if degree not in note_map:
            raise ValueError(f"Invalid degree: {degree}")
        return note_map[degree]

    def get_chord_quality_for_degree(self, degree: int) -> str:
        # Fake logic: even -> "MAJOR", odd -> "MINOR"
        return "MAJOR" if degree % 2 == 0 else "MINOR"

    def get_scale_notes(self) -> List[Note]:
        # Just return the classic 7 notes for test
        return [
            Note(note_name="C", octave=4, duration=1.0, velocity=100),
            Note(note_name="D", octave=4, duration=1.0, velocity=100),
            Note(note_name="E", octave=4, duration=1.0, velocity=100),
            Note(note_name="F", octave=4, duration=1.0, velocity=100),
            Note(note_name="G", octave=4, duration=1.0, velocity=100),
            Note(note_name="A", octave=4, duration=1.0, velocity=100),
            Note(note_name="B", octave=4, duration=1.0, velocity=100),
        ]


class TestChordProgression(unittest.TestCase):
    def test_create_chord_progression_valid_data(self):
        logger.debug("Starting test_create_chord_progression_valid_data")
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="D", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MINOR),
            Chord(root=Note(note_name="E", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.DIMINISHED)
        ]
        logger.debug(f"Chords being created: {[str(chord) for chord in chords]}")
        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type="MAJOR",
            scale_info=ScaleInfo(root=Note(note_name='C', octave=4), scale_type='MAJOR'),
            complexity=0.5
        )
        logger.debug(f"Created progression: {progression}")
        assert progression.name == "Test Progression"
        assert len(progression.chords) == 3
        assert progression.scale_info.root.note_name == 'C'
        assert progression.complexity == 0.5

    def test_invalid_chord_progression_creation(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Invalid Progression",
                chords=[
                    Chord(root=Note(note_name='C', octave=4, duration=1, velocity=100), quality=ChordQualityType.MAJOR)
                ],
                scale_info=ScaleInfo(root=Note(note_name='C', octave=4), scale_type='MAJOR'),
                complexity=0.5
            )

    def test_invalid_complexity(self):
        with self.assertRaises(ValueError, match='Complexity must be between 0 and 1'):
            ChordProgression(
                name="Invalid Complexity",
                chords=[Chord(root=Note(note_name='C', octave=4, duration=1, velocity=100), quality=ChordQualityType.MAJOR)],
                scale_info=ScaleInfo(root=Note(note_name='C', octave=4, duration=1, velocity=100), scale_type='MAJOR'),
                complexity=2.0
            )

    def test_create_chord_progression(self):
        scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), scale_type="MAJOR")
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        progression = ChordProgression(
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type="MAJOR",
            scale_info=scale_info,
            complexity=0.5
        )
        assert progression.get_all_chords() == chords

    def test_add_chord(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                {
                    'root': Note(note_name="C", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                },
                {
                    'root': Note(note_name="F", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                }
            ],
            key="C",
            scale_type="MAJOR",
            complexity=0.5,
            scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
        )
        new_chord = {
            'root': Note(note_name="G", octave=4, duration=1.0, velocity=100),
            'quality': 'MAJOR'
        }
        progression.add_chord(new_chord)
        assert len(progression.chords) == 3
        assert progression.chords[-1] == new_chord

    def test_get_chord_at(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type="MAJOR",
            complexity=0.5,
            scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
        )
        logger.debug(f"Chord at 0: {progression.get_chord_at(0)}")
        assert progression.get_chord_at(0) == progression.chords[0]  

        logger.debug(f"Chord at 1: {progression.get_chord_at(1)}")
        assert progression.get_chord_at(1) == progression.chords[1]  

        logger.debug(f"Chord at 2: {progression.get_chord_at(2)}")
        assert progression.get_chord_at(2) == progression.chords[2]  
        

    def test_get_all_chords(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type="MAJOR",
            complexity=0.5,
            scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
        )
        logger.debug(f"All chords: {progression.get_all_chords()}")
        assert progression.get_all_chords() == progression.chords

    def test_get_chord_names(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                {
                    'root': Note(note_name="C", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                },
                {
                    'root': Note(note_name="F", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                },
                {
                    'root': Note(note_name="G", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                }
            ],
            key="C",
            scale_type="MAJOR",
            complexity=0.5,
            scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
        )
        chord_names = progression.get_chord_names()
        assert chord_names == ["C", "F", "G"]

    def test_model_dump(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type="MAJOR",
            complexity=0.5,
            scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
        )
        assert progression.to_dict() == {
            'id': "test_progression_id",
            'name': "Test Progression",
            'chords': [chord.to_dict() for chord in progression.chords],  # Ensure this matches the actual output
            'key': "C",
            'scale_type': "MAJOR",
            'complexity': 0.5,
        }

    def test_to_dict(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                {
                    'root': Note(note_name="C", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                },
                {
                    'root': Note(note_name="F", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                },
                {
                    'root': Note(note_name="G", octave=4, duration=1.0, velocity=100),
                    'quality': 'MAJOR'
                }
            ],
            key="C",
            scale_type="MAJOR",
            complexity=0.5,
            scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
        )
        assert progression.to_dict() == {
            'id': "test_progression_id",
            'name': "Test Progression",
            'chords': ["C MAJOR", "F MAJOR", "G MAJOR"],  # Updated to match the string representation
            'key': "C",
            'scale_type': "MAJOR",
            'complexity': 0.5,
        }


  

    def test_invalid_chords(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                id="test_progression_id",
                name="Test Progression",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality="invalid_quality"),
                    Chord(root=Note(note_name="D", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MINOR)
                ],
                key="C",
                scale_type="MAJOR",
                complexity=0.5,
                scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
            )

    def test_empty_chords(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                id="test_progression_id",
                name="Test Progression",
                chords=[],  
                key="C",
                scale_type="MAJOR",
                complexity=0.5,
                scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
            )
            logger.debug("Empty chords")

    def test_invalid_complexity(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                id="test_progression_id",
                name="Test Progression",
                chords=[
                    {
                        'root': Note(note_name="C", octave=4, duration=1.0, velocity=100),
                        'quality': 'MAJOR'
                    }
                ],
                key="C",
                scale_type="MAJOR",
                complexity=2.0,  
                scale_info=FakeScaleInfo(root=Note(note_name="C", octave=4), scale_type="MAJOR")
            )
            logger.debug("Invalid complexity")

    def test_chord_progression_initialization(self):
        progression = ChordProgression(
            id='progression_1',
            name='I-IV-V',
            chords=[
                Chord(root=Note(note_name='C', octave=4), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name='F', octave=4), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name='G', octave=4), quality=ChordQualityType.MAJOR)
            ],
            key='C',
            scale_type='MAJOR',
            complexity=0.5
        )
        assert len(progression.chords) == 3  # Ensure chords are initialized correctly

if __name__ == "__main__":
    unittest.main()