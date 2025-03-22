import pytest
import math
from pydantic import BaseModel, ValidationError, field_validator
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.patterns import NotePattern, NotePatternData
from note_gen.models.note import Note
from note_gen.core.enums import ScaleType
from typing import List, Dict, Any
import unittest

class TestPatternValidation(unittest.TestCase):
    def test_rhythm_pattern_validation(self):
        """Test rhythm pattern validation."""
        # Test valid pattern
        valid_pattern = RhythmPattern(
            name="Test Pattern",
            pattern=[
                RhythmNote(position=0.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=1.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=2.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=3.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0)
            ],
            time_signature="4/4",
            description="Test description",
            complexity=0.5,
            data={}
        )
        assert len(valid_pattern.pattern) == 4

    def test_note_pattern_validation(self):
        """Test note pattern validation."""
        valid_pattern = RhythmPattern(
            name="Test Pattern",
            pattern=[
                RhythmNote(position=0.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=1.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=2.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=3.0, duration=1.0, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0)
            ],
            time_signature="4/4",
            description="Test description",
            complexity=0.5,
            data=NotePatternData(
                intervals=[2, 2, 1, 2, 2, 2, 1],
                notes=[
                    Note(note_name="C", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="D", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="E", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="F", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="G", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="A", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="B", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False)
                ],
                scale_type=ScaleType.MAJOR,
                root_note="C"
            )
        )
        assert len(valid_pattern.pattern) == 4
        assert valid_pattern.data.scale_type == ScaleType.MAJOR

        # Test invalid scale type
        with pytest.raises(ValidationError) as cm:
            NotePatternData(
                intervals=[2, 2, 1, 2, 2, 2, 1],
                notes=[
                    Note(note_name="C", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="D", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="E", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="F", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="G", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="A", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="B", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False)
                ],
                scale_type="INVALID",
                root_note="C"
            )
        self.assertIn("Input should be 'MAJOR', 'MINOR', 'HARMONIC_MINOR', 'MELODIC_MINOR', 'DORIAN', 'PHRYGIAN', 'LYDIAN', 'MIXOLYDIAN', 'LOCRIAN' or 'CHROMATIC'", str(cm.value))

        # Test invalid note
        with pytest.raises(ValidationError) as cm:
            NotePatternData(
                intervals=[2, 2, 1, 2, 2, 2, 1],
                notes=[
                    Note(note_name="C", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="D", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="E", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="F", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="G", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="A", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="INVALID", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False)
                ],
                scale_type=ScaleType.MAJOR,
                root_note="C"
            )
        self.assertIn("Input should be 'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'E#', 'Fb', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B', 'B#', 'Cb'", str(cm.value))

        # Test invalid interval
        with pytest.raises(ValidationError) as cm:
            NotePatternData(
                intervals=[2, 2, 1, 2, 2, 2, 13],  # Using an invalid interval value (too large)
                notes=[
                    Note(note_name="C", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="D", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="E", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="F", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="G", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="A", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="B", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False)
                ],
                scale_type=ScaleType.MAJOR,
                root_note="C"
            )
        self.assertIn("All intervals must be integers between 1 and 12", str(cm.value))

        # Test invalid interval (non-integer value)
        with pytest.raises(ValidationError) as cm:
            NotePatternData(
                intervals=[2, 2, 1, 2, 2, 2, "INVALID"],  # Using a non-integer value
                notes=[
                    Note(note_name="C", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="D", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="E", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="F", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="G", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="A", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                    Note(note_name="B", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False)
                ],
                scale_type=ScaleType.MAJOR,
                root_note="C"
            )
        self.assertIn("All intervals must be integers between 1 and 12", str(cm.value))

        # Test valid interval
        valid_pattern = NotePatternData(
            intervals=[2, 2, 1, 2, 2, 2, 1],  # Valid major scale intervals
            notes=[
                Note(note_name="C", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                Note(note_name="D", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                Note(note_name="E", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                Note(note_name="F", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                Note(note_name="G", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                Note(note_name="A", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False),
                Note(note_name="B", octave=4, duration=1.0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None, prefer_flats=False)
            ],
            scale_type=ScaleType.MAJOR,
            root_note="C"
        )
        assert valid_pattern.intervals == [2, 2, 1, 2, 2, 2, 1]

    def test_pattern_duration_validation(self):
        """Test pattern duration validation."""
        pattern = RhythmPattern(
            name="Duration Pattern",
            pattern=[
                RhythmNote(position=0.0, duration=0.5, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=0.5, duration=0.5, velocity=64, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0)
            ],
            time_signature="2/4",
            description="Duration pattern",
            complexity=0.5,
            data={}
        )
        assert len(pattern.pattern) == 2

    def test_rhythm_note_validation(self):
        """Test rhythm note validation."""
        note = RhythmNote(
            position=0.0,
            duration=0.5,
            velocity=64,
            accent=False,
            tuplet_ratio=(1, 1),
            groove_offset=0.0,
            groove_velocity=1.0
        )
        assert note.position == 0.0
        assert note.duration == 0.5
        assert note.velocity == 64
        assert note.accent is False
        assert note.tuplet_ratio == (1, 1)
        assert note.groove_offset == 0.0
        assert note.groove_velocity == 1.0

    def test_tuplet_validation(self):
        """Test tuplet validation."""
        pattern = RhythmPattern(
            name="Tuplet Pattern",
            pattern=[
                RhythmNote(position=0.0, duration=0.5, velocity=64, accent=False, tuplet_ratio=(3, 2), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=0.5, duration=0.5, velocity=64, accent=False, tuplet_ratio=(3, 2), groove_offset=0.0, groove_velocity=1.0),
                RhythmNote(position=1.0, duration=0.5, velocity=64, accent=False, tuplet_ratio=(3, 2), groove_offset=0.0, groove_velocity=1.0)
            ],
            time_signature="3/8",
            description="Tuplet pattern",
            complexity=0.7,
            data={}
        )
        assert pattern.pattern[0].tuplet_ratio == (3, 2)

    def test_type_safety(self):
        """Test type safety."""
        with pytest.raises(ValidationError) as cm:
            RhythmPattern(
                name="Type Safety",
                pattern=[
                    RhythmNote(position=0.0, duration=0.5, velocity=128, accent=False, tuplet_ratio=(1, 1), groove_offset=0.0, groove_velocity=1.0)
                ],
                time_signature="2/4",
                description="Type safety",
                complexity=0.5,
                data={}
            )
        self.assertIn("Input should be less than or equal to 127", str(cm.value))
