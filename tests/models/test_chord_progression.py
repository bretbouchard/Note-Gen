import unittest
from typing import List
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.scale_info import ScaleInfo
from note_gen.models.enums import ChordQualityType
from note_gen.models.musical_elements import Chord, Note
from note_gen.models.scale import ScaleType
import logging

logging.basicConfig(level=logging.DEBUG)


class FakeScaleInfo(ScaleInfo):
    """A fake ScaleInfo that returns placeholder notes for scale degrees."""

    def get_scale_degree_note(self, degree: int) -> Note:
        # Just map 1->C, 2->D, etc. If out of range, raise ValueError.
        note_map = {
            1: Note(note_name="C"),
            2: Note(note_name="D"),
            3: Note(note_name="E"),
            4: Note(note_name="F"),
            5: Note(note_name="G"),
            6: Note(note_name="A"),
            7: Note(note_name="B"),
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
            Note(note_name="C"),
            Note(note_name="D"),
            Note(note_name="E"),
            Note(note_name="F"),
            Note(note_name="G"),
            Note(note_name="A"),
            Note(note_name="B"),
        ]


class TestChordProgression(unittest.TestCase):
    def test_create_chord_progression(self):
        progression = ChordProgression(
            name="Test Progression",
            chords=["C", "F", "G"],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        assert progression.name == "Test Progression"
        assert progression.chords == ["C", "F", "G"]
        assert progression.key == "C"
        assert progression.scale_type == "major"
        assert progression.complexity == 0.5

    def test_add_chord(self):
        progression = ChordProgression(
            name="Test Progression",
            chords=["C", "F"],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        progression.add_chord("G")
        assert progression.chords == ["C", "F", "G"]

    def test_get_chord_at(self):
        progression = ChordProgression(
            name="Test Progression",
            chords=["C", "F", "G"],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        assert progression.get_chord_at(0) == "C"
        assert progression.get_chord_at(1) == "F"
        assert progression.get_chord_at(2) == "G"

    def test_get_all_chords(self):
        progression = ChordProgression(
            name="Test Progression",
            chords=["C", "F", "G"],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        assert progression.get_all_chords() == ["C", "F", "G"]

    def test_get_chord_names(self):
        progression = ChordProgression(
            name="Test Progression",
            chords=["C", "F", "G"],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        assert progression.get_chord_names() == ["C", "F", "G"]

    def test_to_dict(self):
        progression = ChordProgression(
            name="Test Progression",
            chords=["C", "F", "G"],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        progression_dict = progression.to_dict()
        assert progression_dict["chords"] == ["C", "F", "G"]

    def test_model_dump(self):
        progression = ChordProgression(
            name="Test Progression",
            chords=["C", "F", "G"],
            key="C",
            scale_type="major",
            complexity=0.5
        )
        dumped = progression.model_dump()
        assert dumped["chords"] == ["C", "F", "G"]
        assert dumped["name"] == "Test Progression"
        assert dumped["key"] == "C"
        assert dumped["scale_type"] == "major"
        assert dumped["complexity"] == 0.5

    def test_invalid_chords(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Test Progression",
                chords=[1, 2, 3],  # Invalid chord types
                key="C",
                scale_type="major",
                complexity=0.5
            )

    def test_empty_chords(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Test Progression",
                chords=[],  # Empty chords list
                key="C",
                scale_type="major",
                complexity=0.5
            )

    def test_invalid_complexity(self):
        with self.assertRaises(ValueError):
            ChordProgression(
                name="Test Progression",
                chords=["C", "F", "G"],
                key="C",
                scale_type="major",
                complexity=2.0  # Invalid complexity value
            )

if __name__ == "__main__":
    unittest.main()