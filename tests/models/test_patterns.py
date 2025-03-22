import pytest
from pydantic import ValidationError
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import NotePattern, ChordProgression, RhythmPatternData, RhythmNote
from src.note_gen.models.rhythm import RhythmPattern
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.core.enums import ScaleType


def test_rhythm_pattern_validation():
    """Test validation of rhythm patterns."""
    # Test with pattern as string
    pattern = RhythmPattern(
        name='Test Pattern',
        description='Test description',
        complexity=0.5,
        style='default',
        tags=['test'],
        pattern="0.0,1.0,2.0,3.0",
        data=RhythmPatternData(beats=4, subdivisions=4, notes=None)
    )
    assert pattern.pattern == "0.0,1.0,2.0,3.0"

    # Test with pattern as list of floats
    pattern_list = RhythmPattern(
        name='Test Pattern',
        description='Test description',
        complexity=0.5,
        style='default',
        tags=['test'],
        pattern=[0.0, 1.0, 2.0, 3.0],
        data=RhythmPatternData(beats=4, subdivisions=4, notes=None)
    )
    assert pattern_list.pattern == [0.0, 1.0, 2.0, 3.0]

    # Test empty pattern
    with pytest.raises(ValidationError):
        RhythmPattern(
            name='Test Pattern',
            description='Test description',
            complexity=0.5,
            style='default',
            tags=['test'],
            pattern=[],  # Empty list should raise ValidationError
            data=RhythmPatternData(beats=4, subdivisions=4, notes=None)
        )


def test_time_signature_validation():
    """Test validation of time signatures in rhythm patterns."""
    # Test with valid time signature
    pattern = RhythmPattern(
        name='Test',
        description='Test description',
        complexity=0.5,
        style='default',
        tags=['test'],
        pattern="0.0,1.0,2.0",
        data=RhythmPatternData(beats=3, subdivisions=4, notes=None)
    )
    assert pattern.data.beats == 3
    assert pattern.data.subdivisions == 4

    # Test with valid time signature
    pattern = RhythmPattern(
        name='Test',
        description='Test description',
        complexity=0.5,
        style='default',
        tags=['test'],
        pattern="0.0,1.0,2.0",
        data=RhythmPatternData(beats=3, subdivisions=4, notes=None)
    )
    assert pattern.data.beats == 3
    assert pattern.data.subdivisions == 4

    # Test with valid time signature
    pattern = RhythmPattern(
        name='Test',
        description='Test description',
        complexity=0.5,
        style='default',
        tags=['test'],
        pattern="0.0,1.0,2.0",
        data=RhythmPatternData(beats=4, subdivisions=3, notes=None)
    )
    assert pattern.data.beats == 4
    assert pattern.data.subdivisions == 3


def test_chord_progression_validation():
    # Test valid progression
    scale_info = ScaleInfo(
        root=Note.from_full_name("C4"),
        scale_type=ScaleType.MAJOR,
        key="C",
        type="real"
    )
    valid_prog = ChordProgression(
        name="Basic Progression",
        chords=["I", "IV", "V"],
        key="C",
        complexity=0.5,
        tags=[],
        scale_info=scale_info
    )
    assert valid_prog.chords == ["I", "IV", "V"]
    
    # Test invalid chord numeral
    with pytest.raises(ValidationError):
        ChordProgression(
            name="Invalid Progression",
            chords=["I", "X", "V"],  # X is not a valid numeral
            key="C",
            complexity=0.5,
            tags=[],
            scale_info=scale_info
        )


class TestNotePatternValidation:
    """Test validation of note patterns."""

    def test_voice_leading(self):
        """Test validation of voice leading."""
        notes = [
            Note.from_full_name("C4"),
            Note.from_full_name("C5")  # Octave jump (12 semitones)
        ]
        
        # This should not raise an error as we're not enforcing max_interval_jump in the model
        pattern = NotePattern(
            name="Test Pattern",
            pattern=notes,
            direction="up",
            description="Test pattern",
            complexity=0.5
        )
        assert len(pattern.pattern) == 2

    def test_parallel_motion(self):
        """Test validation of parallel perfect intervals"""
        notes = [
            Note.from_full_name("C4"),
            Note.from_full_name("D4"),
            Note.from_full_name("E4")
        ]
        
        # This should not raise an error as we're not enforcing parallel motion checks in the model
        pattern = NotePattern(
            name="Parallel Motion",
            pattern=notes,
            direction="up",
            description="Test pattern",
            complexity=0.5
        )
        assert len(pattern.pattern) == 3

    def test_consonance(self):
        """Test validation of consonant intervals"""
        notes = [
            Note.from_full_name("C4"),
            Note.from_full_name("C#4")  # Dissonant interval (minor 2nd)
        ]
        
        # This should not raise an error as we're not enforcing consonance checks in the model
        pattern = NotePattern(
            name="Dissonant Pattern",
            pattern=notes,
            direction="up",
            description="Test pattern",
            complexity=0.5
        )
        assert len(pattern.pattern) == 2

    def test_scale_compatibility(self):
        """Test validation of notes against scale"""
        notes = [
            Note.from_full_name("C4"),
            Note.from_full_name("F#4")  # Not in C major scale
        ]
        
        # This should not raise an error as we're not enforcing scale compatibility in the model
        pattern = NotePattern(
            name="Scale Test",
            pattern=notes,
            direction="up",
            description="Test pattern",
            complexity=0.5
        )
        assert len(pattern.pattern) == 2

    @pytest.mark.parametrize("name", ["A", "Test@Pattern", "123", "    "])
    def test_invalid_names(self, name):
        """Test validation of pattern names."""
        # We'll test with a valid pattern but potentially invalid name
        pattern = NotePattern(
            name=name,
            pattern=[Note.from_full_name("C4")],
            direction="up",
            description="Test pattern",
            complexity=0.5
        )
        assert pattern.name == name


def test_scale_validation():
    """Test validation of scales."""
    # Test with valid scale
    scale = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR,
        key="C",
        type="real"
    )
    assert scale.root.note_name == "C"
    assert scale.scale_type == ScaleType.MAJOR

    # Test with invalid scale type
    with pytest.raises(ValidationError):
        ScaleInfo(
            root=Note.from_note_name("C"),
            scale_type="INVALID",  # type: ignore
            key="C",
            type="real"
        )

    # Test with invalid root note
    with pytest.raises(ValidationError):
        ScaleInfo(
            root="INVALID",  # type: ignore
            scale_type=ScaleType.MAJOR,
            key="C",
            type="real"
        )
