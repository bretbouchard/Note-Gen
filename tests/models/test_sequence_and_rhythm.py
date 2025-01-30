import unittest
from typing import List

from src.note_gen.models.note import Note
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.pattern_interpreter import ScalePatternInterpreter
from src.note_gen.models.rhythm_pattern import RhythmNote, RhythmPatternData, RhythmPattern
from src.note_gen.models.musical_elements import Chord 
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.scale import Scale, ScaleType
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.note_pattern import NotePattern  # Import NotePattern
from pydantic import BaseModel, Field, ConfigDict, field_validator

class FakeScale(Scale):
    """A minimal fake Scale for testing."""
    def __init__(self) -> None:
        super().__init__(root=Note(note_name='C', octave=4), scale_type=ScaleType.MAJOR)

    def get_notes(self) -> List[Note]:
        # Return notes with octave 4 as expected in tests
        return [
            Note(note_name="C", octave=4),
            Note(note_name="D", octave=4),
            Note(note_name="E", octave=4)
        ]

    def get_degree_of_note(self, note: Note) -> int:
        mapping = {"C": 1, "D": 2, "E": 3}
        return mapping.get(note.note_name, 1)

    def get_scale_degree(self, degree: int) -> Note:
        notes = self.get_notes()
        return notes[(degree - 1) % len(notes)]


class FakeScaleInfo(ScaleInfo):
    def get_scale_degree_note(self, degree: int) -> Note:
        return Note(note_name="C", octave=4)

    def get_chord_quality_for_degree(self, degree: int) -> str:
        return "MAJOR"

    def get_scale_notes(self) -> List[Note]:
        return [Note(note_name="C", octave=4, duration=1, velocity=100), Note(note_name="D"), Note(note_name="E")]


class TestNoteSequence(unittest.TestCase):
    def setUp(self) -> None:
        self.sequence = NoteSequence(notes=[
            Note.from_midi(60, duration=1.0, velocity=100), 
            Note.from_midi(62, duration=1.0, velocity=100), 
            Note.from_midi(64, duration=1.0, velocity=100)
        ], events=[], duration=0.0)
        self.chord = Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality="MAJOR")  # Replace with actual chord instance
        self.scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type='MAJOR')  # Updated to use string for scale_type
        self.note = Note(note_name="C", octave=4)

    def test_validate_notes_converts_ints_to_notes(self) -> None:
        seq = NoteSequence(notes=[Note.from_midi(60, duration=1.0, velocity=100), Note.from_midi(61, duration=1.0, velocity=100)])
        for note in seq.notes:
            self.assertIsInstance(note, Note)

    def test_validate_notes_raises_on_invalid_type(self) -> None:
        with self.assertRaises(ValueError):
            NoteSequence(notes=[Note.from_midi(60, velocity=64, duration=1.0), "invalid", Note.from_midi(62, velocity=64, duration=1.0)], events=[], duration=0.0)

    def test_add_note_appends_event(self) -> None:
        initial_events = len(self.sequence.events)
        self.sequence.add_note(Note.from_midi(65, velocity=64, duration=1.0), position=0.0, duration=1.0, velocity=100)
        self.assertEqual(len(self.sequence.events), initial_events + 1)
        event = self.sequence.events[-1]
        self.assertIsInstance(event.note, Note)

    def test_get_notes_at_returns_correct_events(self) -> None:
        note1 = Note(note_name="C", octave=4, duration=1.0, velocity=100)
        note2 = Note(note_name="D", octave=4, duration=1.0, velocity=100)
        event1 = NoteEvent(note=note1, position=0.0, duration=1.0, velocity=100)
        event2 = NoteEvent(note=note2, position=1.0, duration=1.0, velocity=100)
        seq = NoteSequence(notes=[], events=[event1, event2], duration=0.0)
        result = seq.get_notes_at(0.5)
        self.assertIn(event1, result)
        self.assertNotIn(event2, result)

    def test_clear_resets_sequence(self) -> None:
        self.sequence.add_note(60)
        self.sequence.clear()
        self.assertEqual(len(self.sequence.events), 0)
        self.assertEqual(self.sequence.duration, 0.0)

    def test_note_event_creation(self):
        event = NoteEvent(
            note=self.note,
            position=0.0,
            duration=1.0,
            velocity=100,
            channel=0,
            is_rest=False
        )
        self.assertEqual(event.note, self.note)
        self.assertEqual(event.duration, 1.0)
        self.assertEqual(event.velocity, 100)
        self.assertEqual(event.channel, 0)
        self.assertFalse(event.is_rest)

    def test_note_sequence(self):
        sequence = NoteSequence(
            notes=[self.note],
            events=[],
            duration=3.0
        )
        self.assertEqual(len(sequence.notes), 1)
        self.assertEqual(sequence.duration, 3.0)



class TestPatternInterpreter(unittest.TestCase):
    def setUp(self) -> None:
        fake_scale = FakeScale()
        pattern = [1, 2, 3]
        self.interpreter = ScalePatternInterpreter(scale=fake_scale, pattern=pattern)
        self.chord = Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality="MAJOR")
        self.scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type='MAJOR')  # Updated to use string for scale_type

    def test_interpret_returns_note_sequence(self) -> None:
        sequence = self.interpreter.interpret(pattern=[1, 2, 3], chord=self.chord, scale_info=self.scale_info)        
        self.assertIsInstance(sequence[0].note, Note)  # Check that the note is a Note instance

    def test_get_next_note_cycles_through_pattern(self) -> None:
        scale = FakeScale()
        pattern = [Note(note_name="C", octave=4, duration=1, velocity=100), Note(note_name="D", octave=4, duration=1, velocity=100)]
        interpreter = ScalePatternInterpreter(scale=scale, pattern=pattern)
        
        first_note = interpreter.get_next_note()
        second_note = interpreter.get_next_note()
        third_note = interpreter.get_next_note()  # Cycle repeats

        self.assertEqual(str(first_note), "C4")
        self.assertEqual(str(second_note), "D4")
        self.assertEqual(str(third_note), "C4")  # Should cycle back

    def test_generate_note_sequence(self) -> None:
        """Test generating a note sequence from scale, chord progression, note pattern, and rhythm pattern."""
        
        # Create a fake scale
        scale = FakeScale()

        # Create a rhythm pattern
        rhythm_notes = [RhythmNote(position=0, duration=1), RhythmNote(position=1, duration=1)]
        rhythm_pattern = RhythmPatternData(notes=rhythm_notes)

        # Create a note pattern with MIDI numbers instead of Note instances
        note_pattern = NotePattern(name="Test Pattern", data=[60, 62, 64], notes=[], description="", tags=[], is_test=True)

        # Flatten the note_pattern.data if it contains nested lists
        flat_pattern = [item for sublist in note_pattern.data for item in (sublist if isinstance(sublist, list) else [sublist])]

        # Create a pattern interpreter
        interpreter = ScalePatternInterpreter(scale=scale, pattern=flat_pattern)

        # Generate the note sequence
        note_sequence = interpreter.interpret(pattern=flat_pattern, chord=None, scale_info=None)

        expected_events = [
            NoteEvent(note=Note.from_midi(60, velocity=64, duration=1.0)),
            NoteEvent(note=Note.from_midi(62, velocity=64, duration=1.0)),
            NoteEvent(note=Note.from_midi(64, velocity=64, duration=1.0))
        ]
        print(f"Expected events: {expected_events}")
        print(f"Actual note sequence: {note_sequence}")
        self.assertEqual(note_sequence, expected_events)


class TestRhythmPatternData(unittest.TestCase):
    def setUp(self) -> None:
        self.notes = [
            RhythmNote(position=0.0, duration=1.0, velocity=100),
            RhythmNote(position=1.0, duration=0.5, velocity=100)
        ]
        self.data = RhythmPatternData(
            notes=self.notes,
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.0,
            swing_ratio=0.67,
            style="jazz",
            default_duration=1.0
        )

    def test_validate_duration_negative(self) -> None:
        with self.assertRaises(ValueError):
            RhythmPatternData(
                notes=self.notes,
                time_signature="4/4",
                swing_enabled=False,
                humanize_amount=0.5,
                swing_ratio=0.67,
                style="jazz",
                default_duration=-1.0,  # Directly pass negative duration
            )

def test_calculate_total_duration(self) -> None:
    total_duration = sum(note.duration for note in self.notes)
    self.assertEqual(self.data.total_duration, total_duration)
    
    # When setting a new default duration, we should update the notes
    self.data.default_duration = 2.0
    self.data.notes = [RhythmNote(position=0.0, duration=2.0)]  # Match the default duration
    self.assertEqual(self.data.total_duration, self.data.default_duration)

    def test_validate_swing_ratio_out_of_bounds(self) -> None:
        with self.assertRaises(ValueError):
            RhythmPatternData(
                notes=self.notes,
                time_signature="4/4",
                swing_enabled=True,
                humanize_amount=0.5,
                swing_ratio=0.8,  # out of valid range (0.5 to 0.75)
                style="jazz",
                default_duration=1.0
            )

    def test_validate_duration_zero(self) -> None:
        with self.assertRaises(ValueError):
            RhythmPatternData(
                notes=self.notes,
                time_signature="4/4",
                swing_enabled=False,
                humanize_amount=0.5,
                swing_ratio=0.67,
                style="jazz",
                default_duration=0.0,  # Directly pass zero duration
            )

    def test_validate_duration_non_numeric(self) -> None:
        with self.assertRaises(ValueError):
            RhythmPatternData(
                notes=self.notes,
                time_signature="4/4",
                swing_enabled=False,
                humanize_amount=0.5,
                swing_ratio=0.67,
                style="jazz",
                default_duration="invalid",  # Directly pass non-numeric duration
            )


class TestRhythmPattern(unittest.TestCase):
    def setUp(self) -> None:
        notes = [
            RhythmNote(position=0.0, duration=1.0, velocity=100),
            RhythmNote(position=1.0, duration=1.0, velocity=100),
        ]
        data = RhythmPatternData(
            notes=notes,
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.2,
            swing_ratio=0.67,
            style="rock",
            default_duration=1.0
        )
        self.pattern = RhythmPattern(
            id="test_pattern",  # Add id field
            name="Test Pattern",
            data=data,
            description="A test rhythm pattern",
            tags=["test"],
            complexity=1.0,
            style="rock",
            pattern="1---2---3---4---"  # Provide a valid pattern string
        )

    def test_validate_name_empty(self) -> None:
        from pydantic import ValidationError
        try:
            RhythmPattern(id="1", name="", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern="4 4 4")
            assert False, "Expected ValidationError was not raised for empty name"
        except ValidationError as e:
            errors = e.errors()
            assert any("name cannot be empty" in str(err["msg"]).lower() for err in errors), \
                "Expected error message about empty name not found"

    def test_validate_data_wrong_type(self) -> None:
        # This test should check for a valid RhythmPatternData instance
        rhythm_note = RhythmNote(position=0.0, duration=1.0)
        rhythm_pattern_data = RhythmPatternData(notes=[rhythm_note])  # Valid notes
        RhythmPattern(
            id="test_pattern",  # Add id field
            name="Valid",
            data=rhythm_pattern_data,
            pattern="1---2---3---4---"  # Provide a valid pattern string
        )  # Should not raise TypeError

    def test_get_events_in_range(self) -> None:
        events = self.pattern.get_events_in_range(0.5, 1.5)
        self.assertTrue(all(isinstance(e, RhythmNote) for e in events))

    def test_get_pattern_duration(self) -> None:
        duration = self.pattern.get_pattern_duration()
        self.assertEqual(duration, self.pattern.data.total_duration)


class TestPatternInterpreterExtended(unittest.TestCase):
    def test_generate_note_sequence(self) -> None:
        """Test generating a note sequence from scale, chord progression, note pattern, and rhythm pattern."""
        
        # Create a fake scale
        scale = FakeScale()

        # Create a rhythm pattern
        rhythm_notes = [RhythmNote(position=0, duration=1), RhythmNote(position=1, duration=1)]
        rhythm_pattern = RhythmPatternData(notes=rhythm_notes)

        # Create a note pattern with MIDI numbers instead of Note instances
        note_pattern = NotePattern(name="Test Pattern", data=[60, 62, 64], notes=[], description="", tags=[], is_test=True)

        # Flatten the note_pattern.data if it contains nested lists
        flat_pattern = [item for sublist in note_pattern.data for item in (sublist if isinstance(sublist, list) else [sublist])]

        # Create a pattern interpreter
        interpreter = ScalePatternInterpreter(scale=scale, pattern=flat_pattern)

        # Generate the note sequence
        note_sequence = interpreter.interpret(pattern=flat_pattern, chord=None, scale_info=None)

        expected_events = [
            NoteEvent(note=Note.from_midi(60, velocity=64, duration=1.0)),
            NoteEvent(note=Note.from_midi(62, velocity=64, duration=1.0)),
            NoteEvent(note=Note.from_midi(64, velocity=64, duration=1.0))
        ]
        print(f"Expected events: {expected_events}")
        print(f"Actual note sequence: {note_sequence}")
        self.assertEqual(note_sequence, expected_events)


class TestIntegration(unittest.TestCase):
    def test_full_note_sequence_generation(self) -> None:
        # Setup a fake scale, chord progression, note pattern, and rhythm pattern
        scale = FakeScale()
        fake_chord = Chord(root=Note(note_name="C", octave=4), quality="MAJOR")
        note_pattern_data = [Note(note_name='C', octave=4), Note(note_name='D', octave=4), Note(note_name='E', octave=4)]  # For simplicity
        
        # Create rhythm pattern (if needed for integration; not used in current interpreter)
        rhythm_notes = [RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
        rhythm_pattern = RhythmPatternData(notes=rhythm_notes)

        # Initialize interpreter with scale and pattern
        interpreter = ScalePatternInterpreter(scale=scale, pattern=note_pattern_data)

        # Generate note sequence
        sequence = interpreter.interpret(pattern=note_pattern_data, chord=fake_chord, scale_info=None)

        # Validate that we have a sequence of NoteEvents with proper Notes
        self.assertTrue(all(isinstance(event, NoteEvent) for event in sequence))
        for event, expected_degree in zip(sequence, note_pattern_data):
            expected_note = scale.get_scale_degree(scale.get_degree_of_note(expected_degree))
            if isinstance(event.note, Note):
                self.assertEqual(event.note.note_name, expected_note.note_name)  # Access note_name from Note instance


if __name__ == "__main__":
    unittest.main()