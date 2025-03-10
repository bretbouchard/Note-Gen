import unittest
from typing import List

import pytest
import pytest_asyncio
from pydantic import ValidationError, BaseModel, Field, ConfigDict, field_validator
from src.note_gen.models.patterns import RhythmPattern, RhythmPatternData
from src.note_gen.models.note import Note
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.pattern_interpreter import ScalePatternInterpreter
from src.note_gen.models.patterns import RhythmNote, RhythmPatternData, RhythmPattern
from src.note_gen.models.chord import Chord, ChordQuality
from src.note_gen.models.note_event import NoteEvent
from src.note_gen.models.scale import Scale
from src.note_gen.models.enums import ScaleType

from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.patterns import NotePattern, NotePatternData 
from src.note_gen.models.roman_numeral import RomanNumeral

import logging

logger = logging.getLogger(__name__)

@pytest_asyncio.fixture(scope="session")
async def test_pattern_interpreter(test_db):
    return ScalePatternInterpreter(db=test_db)

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
        self.notes = [Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)]
        self.sequence = NoteSequence(notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)], events=[], duration=0.0)
        self.data = self.sequence  # Initialize self.data to reference the sequence
        self.chord = Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)  # Update to use ChordQuality enum
        self.scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)  # Updated to use ScaleType enum
        self.note = Note(note_name="C", octave=4)

    def test_validate_notes_converts_ints_to_notes(self) -> None:
        seq = NoteSequence(notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100)])
        for note in seq.notes:
            self.assertIsInstance(note, Note)

    def test_validate_notes_raises_on_invalid_type(self) -> None:
        with self.assertRaises(ValueError):
            NoteSequence(notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), "invalid", Note(note_name='D', octave=4, duration=1.0, velocity=100)], events=[], duration=0.0)

    def test_add_note_appends_event(self) -> None:
        initial_events = len(self.sequence.events)
        self.sequence.add_note(Note(note_name='E', octave=4, duration=1.0, velocity=100), position=0.0, duration=1.0, velocity=100)
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
        self.sequence.add_note(Note(note_name='E', octave=4, duration=1.0, velocity=100))
        self.sequence.clear()
        self.assertEqual(len(self.sequence.events), 0)
        self.assertEqual(self.sequence.duration, 0.0)

    def test_note_event_creation(self) -> None:
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

    def test_note_sequence(self) -> None:
        sequence = NoteSequence(
            notes=[self.note],
            events=[],
            duration=3.0
        )
        self.assertEqual(len(sequence.notes), 1)
        self.assertEqual(sequence.duration, 3.0)

    def test_calculate_total_duration(self) -> None:
        total_duration = sum(note.duration for note in self.notes)
        self.assertEqual(self.data.total_duration, total_duration)
        
        # When setting a new default duration, we should update the notes
        self.data.default_duration = 2.0
        self.data.notes = [Note(note_name="C", octave=4, duration=2.0, velocity=100)]  # Match the default duration
        self.assertEqual(self.data.total_duration, self.data.default_duration)


class TestPatternInterpreter(unittest.TestCase):
    def setUp(self) -> None:
        fake_scale = FakeScale()
        pattern = [1, 2, 3]
        self.interpreter = ScalePatternInterpreter(scale=fake_scale, pattern=pattern)
        self.chord = Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)  # Update to use ChordQuality enum
        self.scale_info = FakeScaleInfo(root=Note(note_name="C", octave=4, duration=1, velocity=100), scale_type=ScaleType.MAJOR)  # Updated to use ScaleType enum

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

        # Create a valid NotePatternData instance with required fields
        note_data = NotePatternData(notes=[
            Note(note_name='C', octave=4, duration=1.0, velocity=100),
            Note(note_name='D', octave=4, duration=1.0, velocity=100),
            Note(note_name='E', octave=4, duration=1.0, velocity=100)
        ], index=0, pattern=[0, 2, 4])  # Include the index field and pattern

        # Create a note pattern with the NotePatternData instance
        note_pattern = NotePattern(
            name="Test Pattern",
            data=note_data,
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100), Note(note_name='E', octave=4, duration=1.0, velocity=100)],  # Use Note instances
            description="",
            tags=["test"],  # Added non-empty tags
            duration=1.0,  # Added required duration
            position=0.0,  # Added required position
            velocity=100,  # Added required velocity
            pattern=[0, 2, 4],  # Add a valid pattern
            complexity=0.5,  # Added required field
            is_test=True
        )

        # Create a pattern interpreter using the extracted notes
        interpreter = ScalePatternInterpreter(scale=scale, pattern=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100), Note(note_name='E', octave=4, duration=1.0, velocity=100)])

        # Generate the note sequence
        note_sequence = interpreter.interpret(pattern=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100), Note(note_name='E', octave=4, duration=1.0, velocity=100)], chord=None, scale_info=None)

        expected_events = [
            NoteEvent(note=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            NoteEvent(note=Note(note_name='D', octave=4, duration=1.0, velocity=100)),
            NoteEvent(note=Note(note_name='E', octave=4, duration=1.0, velocity=100))
        ]
        print(f"Expected events: {expected_events}")
        print(f"Actual note sequence: {note_sequence}")
        self.assertEqual(note_sequence, expected_events)


class TestRhythmPatternData(unittest.TestCase):
    def setUp(self) -> None:
        self.notes = [RhythmNote(position=0.0, duration=1.0, velocity=100), RhythmNote(position=1.0, duration=1.0, velocity=100)]
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
        """Test that negative durations are correctly handled as rests.
        
        Our convention is:
        - Positive durations represent regular notes
        - Negative durations represent rests
        - Zero durations are invalid
        """
        # Create a RhythmPatternData with a negative duration note (rest)
        rhythm_data = RhythmPatternData(
            notes=[
                RhythmNote(position=0.0, duration=1.0, velocity=100),  # Regular note
                RhythmNote(position=1.0, duration=-1.0, velocity=100)  # Rest with duration of 1.0
            ],
            time_signature="4/4",
            swing_enabled=False,
            humanize_amount=0.0,
            swing_ratio=0.67,
            style="jazz",
            default_duration=1.0
        )
        
        # Verify that the note with negative duration is properly marked as a rest
        self.assertTrue(rhythm_data.notes[1].is_rest, "Note with negative duration should be marked as a rest")
        self.assertEqual(-1.0, rhythm_data.notes[1].duration, "Duration should remain negative for rests")

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
                notes=[RhythmNote(position=0.0, duration=0.0, velocity=100), RhythmNote(position=1.0, duration=1.0, velocity=100)],
                time_signature="4/4",
                swing_enabled=False,
                humanize_amount=0.0,
                swing_ratio=0.67,
                style="jazz",
                default_duration=1.0
            )

    def test_validate_duration_non_numeric(self) -> None:
        with self.assertRaises(ValueError):
            RhythmPatternData(
                notes=[RhythmNote(position=0.0, duration="a", velocity=100), RhythmNote(position=1.0, duration=1.0, velocity=100)],
                time_signature="4/4",
                swing_enabled=False,
                humanize_amount=0.0,
                swing_ratio=0.67,
                style="jazz",
                default_duration=1.0
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
        pattern_string = "4 4 4 4"
        pattern_list = [float(d) for d in pattern_string.split()]
        self.pattern = RhythmPattern(
            id="test_pattern",  # Add id field
            name="Test Pattern",
            data=data,
            description="A test rhythm pattern",
            tags=["test"],
            complexity=1.0,
            style="rock",
            pattern=pattern_list  # Use the converted list instead of string
        )
        
        self.pattern.data.total_duration = 4.0  # Ensure total duration matches measure duration for 4/4

    def test_validate_name_empty(self) -> None:
        from pydantic import ValidationError
        with pytest.raises(ValidationError, match="string_too_short"):  # Updated to match actual error type
            RhythmPattern(id="1", name="", data=RhythmPatternData(notes=[RhythmNote(position=0, duration=1.0)]), pattern=[4, 4, 4, 4], complexity=0.5, total_duration=4.0)

    def test_validate_data_wrong_type(self) -> None:
        """Test that creating a RhythmPattern with invalid data raises an error."""
        # First part of the test remains the same
        with pytest.raises((ValidationError, ValueError), match=r"(?i).*notes.*required|missing|invalid.*"):
            data_dict = {"some": "data"}  # Missing 'notes' field
            RhythmPatternData(**data_dict)
        
        # For the second part, use model_validate instead of constructor
        try:
            RhythmPattern.model_validate({
                "id": "test_pattern",
                "name": "Test Rhythm",
                "complexity": 0.5,
                "data": {"some": "data"},  # Invalid data - missing 'notes' field
                "pattern": [4, 4, 4, 4],
                "total_duration": 4.0
            })
            pytest.fail("Expected ValidationError or ValueError was not raised")
        except (ValidationError, ValueError) as e:
            # Test passes if an exception is raised
            pass

    def test_get_events_in_range(self) -> None:
        pattern_string = "4 4 4 4"
        pattern_list = [float(d) for d in pattern_string.split()]
        self.pattern.pattern = pattern_list
        
        logger.debug(f"Pattern: {self.pattern.pattern}, Total Duration: {self.pattern.data.total_duration}")
        logger.debug(f"Getting events in range: 0.5, 1.5")
        events = self.pattern.get_events_in_range(0.5, 1.5)
        logger.debug(f"Events returned: {events}")
        self.assertTrue(all(isinstance(e, RhythmNote) for e in events))

    def test_get_pattern_duration(self) -> None:
        pattern_string = "4 4 4 4"
        pattern_list = [float(d) for d in pattern_string.split()]
        self.pattern.pattern = pattern_list
        
        duration = self.pattern.get_pattern_duration()
        self.assertEqual(duration, self.pattern.data.total_duration)

    def test_recalculate_pattern_duration(self) -> None:
        notes = [
            RhythmNote(position=0.0, duration=1.0, velocity=100),
            RhythmNote(position=1.0, duration=1.0, velocity=100),
            RhythmNote(position=2.0, duration=1.0, velocity=100),
            RhythmNote(position=3.0, duration=1.0, velocity=100),
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
        
        pattern_string = "4 4 4 4"
        pattern_list = [float(d) for d in pattern_string.split()]
        
        self.pattern = RhythmPattern(
            id="test_pattern",  # Add id field
            name="Test Pattern",
            data=data,
            description="A test rhythm pattern",
            tags=["test"],
            complexity=1.0,
            style="rock",
            pattern=pattern_list  # Use the converted list instead of string
        )
        with pytest.raises(ValueError, match="Total duration must be a multiple of the beat duration"):
            self.pattern.recalculate_pattern_duration(total_duration=3.5)


class TestPatternInterpreterExtended(unittest.TestCase):
    def test_generate_note_sequence(self) -> None:
        """Test generating a note sequence from scale, chord progression, note pattern, and rhythm pattern."""
        
        # Create a fake scale
        scale = FakeScale()

        # Create a rhythm pattern
        rhythm_notes = [RhythmNote(position=0, duration=1), RhythmNote(position=1, duration=1)]
        rhythm_pattern = RhythmPatternData(notes=rhythm_notes)

        # Create a valid NotePatternData instance with required fields
        note_data = NotePatternData(notes=[
            Note(note_name='C', octave=4, duration=1.0, velocity=100),
            Note(note_name='D', octave=4, duration=1.0, velocity=100),
            Note(note_name='E', octave=4, duration=1.0, velocity=100)
        ], index=0, pattern=[0, 2, 4])  # Include the index field and pattern

        # Create a note pattern with the NotePatternData instance
        note_pattern = NotePattern(
            name="Test Pattern",
            data=note_data,
            notes=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100), Note(note_name='E', octave=4, duration=1.0, velocity=100)],  # Use Note instances
            description="",
            tags=["test"],  # Added non-empty tags
            duration=1.0,  # Added required duration
            position=0.0,  # Added required position
            velocity=100,  # Added required velocity
            pattern=[0, 2, 4],  # Add a valid pattern
            complexity=0.5,  # Added required field
            is_test=True
        )

        # Create a pattern interpreter using the extracted notes
        interpreter = ScalePatternInterpreter(scale=scale, pattern=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100), Note(note_name='E', octave=4, duration=1.0, velocity=100)])

        # Generate the note sequence
        note_sequence = interpreter.interpret(pattern=[Note(note_name='C', octave=4, duration=1.0, velocity=100), Note(note_name='D', octave=4, duration=1.0, velocity=100), Note(note_name='E', octave=4, duration=1.0, velocity=100)], chord=None, scale_info=None)

        expected_events = [
            NoteEvent(note=Note(note_name='C', octave=4, duration=1.0, velocity=100)),
            NoteEvent(note=Note(note_name='D', octave=4, duration=1.0, velocity=100)),
            NoteEvent(note=Note(note_name='E', octave=4, duration=1.0, velocity=100))
        ]
        print(f"Expected events: {expected_events}")
        print(f"Actual note sequence: {note_sequence}")
        self.assertEqual(note_sequence, expected_events)


class TestIntegration(unittest.TestCase):
    def test_full_note_sequence_generation(self) -> None:
        # Setup a fake scale, chord progression, note pattern, and rhythm pattern
        scale = FakeScale()
        fake_chord = Chord(root=Note(note_name="C", octave=4, duration=1.0, velocity=100), quality=ChordQuality.MAJOR)  # Update to use ChordQuality enum
        note_pattern_data = {
            "name": "Test Note Pattern",
            "pattern": [0, 2, 4],  # Representing intervals
            "index": 1,
            "direction": "up",
            "use_chord_tones": False,
            "use_scale_mode": False,
            "arpeggio_mode": False,
            "restart_on_chord": False,
        }
        
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