import unittest
from typing import List
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.scale import ScaleType
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
    def test_empty_chords_raises_error(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            ChordProgression(name="Test Progression", scale_info=scale_info, chords=[], key="C")

    def test_chords_must_be_chord_instances(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        with self.assertRaises(ValueError):
            ChordProgression(name="Test Progression", scale_info=scale_info, chords=["not a chord"], key="C")

    def test_add_and_get_chord(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        chord1 = Chord(root=Note(note_name="C"), quality=ChordQualityType.MAJOR)
        progression = ChordProgression(name="Test Progression", scale_info=scale_info, chords=[chord1.dict()], key="C")
        self.assertEqual(progression.get_chord_at(0), chord1.dict())

        chord2 = Chord(root=Note(note_name="D"), quality=ChordQualityType.MINOR)
        progression.add_chord(chord2.dict())
        self.assertEqual(progression.get_chord_at(1), chord2.dict())

    def test_get_all_chords(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C"), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="G"), quality=ChordQualityType.MAJOR),
        ]
        progression = ChordProgression(name="Test Progression", scale_info=scale_info, chords=[c.dict() for c in chords], key="C")
        self.assertEqual(progression.get_all_chords(), [c.dict() for c in chords])

    def test_get_chord_names(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C"), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="D"), quality=ChordQualityType.MINOR),
        ]
        progression = ChordProgression(name="Test Progression", scale_info=scale_info, chords=[c.dict() for c in chords], key="C")
        expected_names = ["I", "ii"]  # Update expected names based on Roman numeral logic
        self.assertEqual(progression.get_chord_names(), expected_names)

    def test_chord_progression_repr(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        chords = [
            Chord(root=Note(note_name="C"), quality=ChordQualityType.MAJOR),
            Chord(root=Note(note_name="D"), quality=ChordQualityType.MINOR),
        ]
        progression = ChordProgression(name="Test Progression", scale_info=scale_info, chords=[c.dict() for c in chords], key="C")
        actual_repr = repr(progression)

        expected_repr = (
            "ChordProgression(scale_info=FakeScaleInfo(root=Note(note_name='C', octave=4, duration=1.0, velocity=64, stored_midi_number=None), scale_type=<ScaleType.MAJOR: 'major'>), "
            "chords=[Chord(root=Note(note_name='C', octave=4, duration=1.0, velocity=64, stored_midi_number=None), quality=<ChordQualityType.MAJOR: 'major'>, "
            "notes=[Note(note_name='C', octave=4, duration=1.0, velocity=64, stored_midi_number=60), Note(note_name='E', octave=4, duration=1.0, velocity=64, stored_midi_number=64), "
            "Note(note_name='G', octave=4, duration=1.0, velocity=64, stored_midi_number=67)], inversion=0, QUALITY_INTERVALS={<ChordQualityType.MAJOR: 'major'>: [0, 4, 7], "
            "<ChordQualityType.MINOR: 'minor'>: [0, 3, 7], <ChordQualityType.DIMINISHED: 'diminished'>: [0, 3, 6], <ChordQualityType.AUGMENTED: 'augmented'>: [0, 4, 8], "
            "<ChordQualityType.DOMINANT: 'dominant'>: [0, 4, 7, 10], <ChordQualityType.MAJOR_7: 'major_7'>: [0, 4, 7, 11], <ChordQualityType.MINOR_7: 'minor_7'>: [0, 3, 7, 10], "
            "<ChordQualityType.HALF_DIMINISHED: 'half_diminished'>: [0, 3, 6, 10], <ChordQualityType.FULLY_DIMINISHED: 'fully_diminished'>: [0, 3, 6, 9]})])"
        )

        self.assertEqual(actual_repr, expected_repr)

    def test_dict_representation(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        chord = Chord(root=Note(note_name="C"), quality=ChordQualityType.MAJOR)
        progression = ChordProgression(name="Test Progression", scale_info=scale_info, chords=[chord.dict()], key="C")
        expected_dict = {
            "scale_info": scale_info.dict(),
            "chords": [chord.dict()]
        }
        self.assertEqual(progression.to_dict(), expected_dict)

    def test_transpose_progression(self) -> None:
        scale_info = FakeScaleInfo(root=Note(note_name="C"), scale_type=ScaleType.MAJOR)
        chord_c = Chord(root=Note(note_name="C", octave=4), quality=ChordQualityType.MAJOR)
        chord_d = Chord(root=Note(note_name="D", octave=4), quality=ChordQualityType.MINOR)
        progression = ChordProgression(name="Test Progression", scale_info=scale_info, chords=[chord_c.dict(), chord_d.dict()], key="C")

        # Transpose up a major third (4 semitones)
        progression.transpose(4)

        # Check that the chords have been transposed correctly
        transposed_chords = progression.get_all_chords()
        self.assertEqual(transposed_chords[0]["root"]["note_name"], "E")  # C -> E
        self.assertEqual(transposed_chords[1]["root"]["note_name"], "F#")  # D -> F#

if __name__ == "__main__":
    unittest.main()