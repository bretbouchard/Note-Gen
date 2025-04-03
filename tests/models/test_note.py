"""Test suite for Note model."""
import pytest
from pydantic import ValidationError
from note_gen.models.note import Note


class TestNote:
    def test_note_creation(self) -> None:
        """Test basic note creation."""
        note = Note(pitch="C", octave=4)
        assert note.pitch == "C"
        assert note.octave == 4
        assert note.pitch_name == "C"  # Changed from note_name to pitch_name
        assert note.full_name == "C4"

    def test_from_midi_number(self) -> None:
        note = Note.from_midi_number(60)  # Middle C
        assert note.pitch == "C"
        assert note.octave == 4
        assert note.stored_midi_number == 60
        assert note.midi_number == 60

    def test_pitch_normalization(self) -> None:
        assert Note.normalize_pitch("C") == "C"
        assert Note.normalize_pitch("c") == "C"
        assert Note.normalize_pitch("F") == "F"
        with pytest.raises(ValueError):
            Note.normalize_pitch("H")

    def test_from_name(self) -> None:
        """Test creating note from string name."""
        note = Note.from_name("C#4")
        assert note.pitch == "C#"
        assert note.octave == 4
        assert note.pitch_name == "C#"  # Changed from note_name to pitch_name
        assert note.full_name == "C#4"

    def test_note_methods(self) -> None:
        """Test note creation and basic methods."""
        note = Note(pitch="B", octave=4, duration=1.0)
        assert note.pitch == "B"
        assert note.octave == 4
        assert note.pitch_name == "B"  # Use pitch_name for just the pitch
        assert note.note_name == "B4"  # Use note_name for full name
        
        with pytest.raises(ValueError, match="Invalid pitch format: H"):
            Note(pitch="H", octave=4, duration=1.0)
        
        note = Note.from_name("C#4", duration=1.0)
        assert note.pitch == "C#"
        assert note.accidental == "#"
        assert note.octave == 4

    def test_note_enharmonics(self) -> None:
        note = Note.from_name("C#4")
        enharmonic = note.get_enharmonic(prefer_flats=True)
        if enharmonic:  # Type guard for mypy
            assert enharmonic.pitch == "Db"
            assert enharmonic.accidental == "b"
            assert enharmonic.octave == 4

    def test_midi_number_validation(self) -> None:
        with pytest.raises(ValueError):
            Note.validate_midi_number(128)
        with pytest.raises(ValueError):
            Note.validate_midi_number(-1)

    def test_midi_number_edge_cases(self) -> None:
        assert Note.from_midi_number(0).midi_number == 0  # Lowest valid MIDI
        assert Note.from_midi_number(127).midi_number == 127  # Highest valid MIDI

    def test_midi_conversion_edge_cases(self) -> None:
        lowest = Note.from_midi_number(0)
        highest = Note.from_midi_number(127)
        assert lowest.midi_number == 0
        assert highest.midi_number == 127

    def test_transposition_limits(self) -> None:
        note = Note(pitch="C", octave=4)
        with pytest.raises(ValueError):
            note.transpose(128)  # Should exceed MIDI range
        with pytest.raises(ValueError):
            note.transpose(-128)  # Should exceed MIDI range

    def test_midi_conversion(self) -> None:
        """Test MIDI number conversion."""
        note = Note(pitch="C", octave=4)
        assert note.midi_number == 60
        assert note.to_midi_number() == 60

    def test_transpose(self) -> None:
        """Test note transposition."""
        note = Note(pitch="C", octave=4)
        transposed = note.transpose(2)
        assert transposed.pitch == "D"
        assert transposed.octave == 4


class TestNoteAdvanced:
    def test_enharmonic_equivalents(self) -> None:
        note = Note(pitch="C#", octave=4)
        enharmonic = note.get_enharmonic(prefer_flats=True)
        if enharmonic:  # Type guard
            assert enharmonic.pitch == "Db"
            assert enharmonic.octave == 4

    def test_note_validation_edge_cases(self) -> None:
        with pytest.raises(ValidationError):
            Note(pitch="", octave=4)
        with pytest.raises(ValidationError):
            Note(pitch="H", octave=4)

    def test_midi_number_validation(self) -> None:
        with pytest.raises(ValueError):
            Note.validate_midi_number(128)

    def test_note_name_parsing(self) -> None:
        assert Note.normalize_pitch("C") == "C"
        assert Note.normalize_pitch("F") == "F"
        with pytest.raises(ValueError):
            Note.normalize_pitch("H")

    def test_note_validation_comprehensive(self) -> None:
        assert Note.normalize_pitch("C") == "C"
        assert Note.normalize_pitch("F") == "F"
        with pytest.raises(ValueError):
            Note.normalize_pitch("H")

    def test_midi_conversion_edge_cases(self) -> None:
        lowest = Note.from_midi_number(0)
        highest = Note.from_midi_number(127)
        assert lowest.midi_number == 0
        assert highest.midi_number == 127

    def test_note_properties_comprehensive(self) -> None:
        note = Note(pitch="C#", octave=4)
        assert note.note_name == "C#4"  # This is now correct
        assert note.pitch_name == "C#"  # Use pitch_name for just the pitch
        assert note.midi_number == 61

    def test_note_factory_methods(self) -> None:
        note = Note.from_midi_number(60, duration=2.0, position=1.0, velocity=100)
        assert note.duration == 2.0
        assert note.position == 1.0
        assert note.velocity == 100


class TestRhythmNote:
    def test_from_name_comprehensive(self) -> None:
        """Test note creation from string name comprehensively"""
        test_cases = [
            ("C4", "C", None, 4),
            ("F#5", "F#", "#", 5),
            ("Bb3", "Bb", "b", 3),
            ("G8", "G", None, 8),
            ("C0", "C", None, 0),
        ]
        
        for note_str, expected_pitch, expected_accidental, expected_octave in test_cases:
            note = Note.from_name(note_str)
            assert note.pitch == expected_pitch
            assert note.accidental == expected_accidental
            assert note.octave == expected_octave

    def test_model_validation_comprehensive(self) -> None:
        """Test comprehensive model validation scenarios"""
        valid_cases = [
            Note(pitch="C", octave=4),
            Note(pitch="F#", octave=5),
            Note(pitch="Bb", octave=3)
        ]
        for note in valid_cases:
            assert isinstance(note, Note)

    def test_get_enharmonic(self) -> None:
        """Test getting enharmonic equivalents of notes."""
        # Test sharp to flat
        note = Note(pitch="C#", octave=4)
        enharmonic = note.get_enharmonic()
        assert enharmonic.pitch == "Db"
        assert enharmonic.octave == 4

        # Test flat to sharp
        note = Note(pitch="Eb", octave=4)
        enharmonic = note.get_enharmonic()
        assert enharmonic.pitch == "D#"
        assert enharmonic.octave == 4

        # Test natural note (should return copy of same note)
        note = Note(pitch="C", octave=4)
        enharmonic = note.get_enharmonic()
        assert enharmonic.pitch == "C"
        assert enharmonic.octave == 4

        # Test that other properties are preserved
        note = Note(
            pitch="F#",
            octave=4,
            duration=2.0,
            velocity=100,
            position=1.5
        )
        enharmonic = note.get_enharmonic()
        assert enharmonic.pitch == "Gb"
        assert enharmonic.duration == 2.0
        assert enharmonic.velocity == 100
        assert enharmonic.position == 1.5
