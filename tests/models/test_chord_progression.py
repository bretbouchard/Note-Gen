import unittest
from typing import List
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.chord_progression import ChordProgression
import logging

logging.basicConfig(level=logging.DEBUG)


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
        # Fake logic: even -> "major", odd -> "minor"
        return "major" if degree % 2 == 0 else "minor"

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
    def test_create_chord_progression(self):
        chords = [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=chords,
            key="C",
            scale_type="major",
            complexity=0.5
        )
        logging.debug(f"Progression: {progression}")
        assert progression.name == "Test Progression"
        assert progression.chords == chords
        assert progression.key == "C"
        assert progression.scale_type == "major"
        assert progression.complexity == 0.5

    def test_add_chord(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        progression.add_chord(Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR))
        logging.debug(f"Progression after adding chord: {progression}")
        assert progression.chords == [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]

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
            scale_type="major",
            complexity=0.5
        )
        logging.debug(f"Chord at 0: {progression.get_chord_at(0)}")
        assert progression.get_chord_at(0) == Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        logging.debug(f"Chord at 1: {progression.get_chord_at(1)}")
        assert progression.get_chord_at(1) == Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        logging.debug(f"Chord at 2: {progression.get_chord_at(2)}")
        assert progression.get_chord_at(2) == Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)

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
            scale_type="major",
            complexity=0.5
        )
        logging.debug(f"All chords: {progression.get_all_chords()}")
        assert progression.get_all_chords() == [
            Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
        ]

    def test_get_chord_names(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        actual_names = progression.get_chord_names()
        logging.debug(f"Actual chord names: {actual_names}")
        assert actual_names == ["C major", "F major", "G major"]

    def test_to_dict(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        progression_dict = progression.to_dict()
        logging.debug(f"Progression dict: {progression_dict}")
        assert progression_dict["chords"] == ["C major", "F major", "G major"]

    def test_model_dump(self):
        progression = ChordProgression(
            id="test_progression_id",
            name="Test Progression",
            chords=[
                Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
            ],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        dumped = progression.model_dump()
        logging.debug(f"Dumped model: {dumped}")
        assert dumped["chords"] == ["C major", "F major", "G major"]
        assert dumped["name"] == "Test Progression"
        assert dumped["key"] == "C"
        assert dumped["scale_type"] == "major"
        assert dumped["complexity"] == 0.5

    def test_invalid_chords(self):
        try:
            progression = ChordProgression(
                id="test_progression_id",
                name="Test Progression",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                    Chord(root=Note(note_name="D", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MINOR),
                    2,  # Invalid chord type
                    Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
                ],
                key="C",
                scale_type="major",
                complexity=0.5
            )
        except ValueError:
            logging.debug('Caught ValueError as expected for invalid chord type.')  # Log the expected error
            return  # Pass the test if ValueError is raised
        self.fail('ValueError not raised for invalid chord type.')  # Fail the test if no error is raised

    def test_empty_chords(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                id="test_progression_id",
                name="Test Progression",
                chords=[],  
                key="C",
                scale_type="major",
                complexity=0.5
            )
            logging.debug("Empty chords")

    def test_invalid_complexity(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                id="test_progression_id",
                name="Test Progression",
                chords=[
                    Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                    Chord(root=Note(note_name="F", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR),
                    Chord(root=Note(note_name="G", octave=4, duration=1.0, velocity=100), quality=ChordQualityType.MAJOR)
                ],
                key="C",
                scale_type="major",
                complexity=2.0  
            )
            logging.debug("Invalid complexity")

if __name__ == "__main__":
    unittest.main()