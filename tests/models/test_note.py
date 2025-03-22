import pytest
import logging
from pydantic import ValidationError, field_validator, ValidationInfo
from src.note_gen.models.note import Note, RhythmNote
from src.note_gen.core.constants import MIDI_MIN, MIDI_MAX, FULL_NOTE_REGEX

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def c4_note():
    return Note(note_name="C", octave=4)

@pytest.fixture
def rhythm_note():
    return RhythmNote(position=0.0, duration=1.0, velocity=64)

class TestNote:
    def test_note_creation(self):
        note = Note(note_name="C", octave=4)
        assert note.note_name == "C"
        assert note.octave == 4
        assert note.duration == 1.0
        assert note.position == 0.0
        assert note.velocity == 64

    def test_note_validation(self):
        with pytest.raises(ValidationError):
            Note(note_name="H", octave=4)  # Invalid note name
        with pytest.raises(ValidationError):
            Note(note_name="C", octave=9)  # Octave too high
        with pytest.raises(ValidationError):
            Note(note_name="C", octave=-1)  # Octave too low

    def test_midi_number_calculation(self, c4_note):
        assert c4_note.midi_number == 60  # C4 should be MIDI 60
        
    def test_from_midi_number(self):
        note = Note.from_midi_number(60)  # Middle C
        assert note.note_name == "C"
        assert note.octave == 4
        assert note.stored_midi_number == 60

    def test_note_name_normalization(self):
        assert Note.normalize_note_name("c") == "C"
        assert Note.normalize_note_name("C#") == "C#"
        assert Note.normalize_note_name("Bb") == "Bb"
        with pytest.raises(ValueError):
            Note.normalize_note_name("H")

    def test_from_name(self):
        note = Note.from_name("C4")
        assert note.note_name == "C"
        assert note.octave == 4
        
        note = Note.from_name("F#5")
        assert note.note_name == "F#"
        assert note.octave == 5
        
        note = Note.from_name("Bb3")
        assert note.note_name == "Bb"
        assert note.octave == 3
        
        with pytest.raises(ValueError):
            Note.from_name("H4")
        with pytest.raises(ValueError):
            Note.from_name("C9")
        with pytest.raises(ValueError):
            Note.from_name("C")

    def test_note_methods(self):
        note = Note(note_name="b", octave=4)
        assert note.note_name == "B"
        
        with pytest.raises(ValueError):
            Note(note_name="H", octave=4)
            
        note = Note(note_name="C#", octave=4)
        assert f"{note.note_name}{note.octave}" == "C#4"
        
        note = Note(note_name="C", octave=4, stored_midi_number=60)
        assert note.midi_number == 60
        assert note.get_midi_number() == 60

    def test_note_enharmonics(self):
        note1 = Note(note_name="C#", octave=4)
        note2 = Note(note_name="Db", octave=4)
        assert note1.midi_number == note2.midi_number
        
        note = Note.from_midi_number(61, prefer_flats=True)
        assert note.note_name == "Db"
        
        note = Note.from_midi_number(61, prefer_flats=False)
        assert note.note_name == "C#"

    def test_note_validation_edge_cases(self):
        """Test validation of edge cases for note creation."""
        with pytest.raises(ValueError):
            Note(note_name="C", octave=9)

    def test_midi_number_validation(self):
        """Test stored_midi_number validation."""
        with pytest.raises(ValueError):
            Note(note_name="C", octave=4, stored_midi_number=61)

    def test_midi_number_edge_cases(self):
        """Test edge cases in MIDI number conversion."""
        # Test valid edge cases
        note = Note(note_name="G", octave=8)
        assert note.midi_number == 127

        # Test invalid MIDI number
        with pytest.raises(ValueError) as exc_info:
            Note(note_name="C", octave=4, stored_midi_number=128)
        assert "128" in str(exc_info.value)  # Just check that the value is mentioned in the error
        assert "MIDI" in str(exc_info.value)  # Make sure it's about MIDI

    def test_midi_conversion_edge_cases(self):
        """Test edge cases in MIDI number conversion."""
        # Test highest valid note (G8 = MIDI 127)
        note = Note(note_name="G", octave=8)
        assert note.midi_number == 127

        # Test invalid notes in octave 8
        for invalid_note in ["A", "G#", "Ab"]:
            with pytest.raises(ValueError) as exc_info:
                Note(note_name=invalid_note, octave=8)
            assert "exceeds MIDI range" in str(exc_info.value)

    def test_transposition_limits(self):
        """Test transposition at the limits of MIDI range."""
        # Test transposing at upper limit
        high_note = Note(note_name="C", octave=8)
        with pytest.raises(ValueError, match="MIDI number out of range"):
            high_note.transpose(1)

        # Test transposing at lower limit
        low_note = Note(note_name="C", octave=0)
        with pytest.raises(ValueError, match="MIDI number out of range"):
            low_note.transpose(-1)

class TestNoteAdvanced:
    def test_fill_missing_fields(self):
        # Test dictionary input
        filled = Note.fill_missing_fields({})
        assert filled["note_name"] == "C"
        assert filled["octave"] == 4

        # Test with invalid dictionary
        with pytest.raises(ValueError, match="Missing required field: note_name"):
            Note.fill_missing_fields({"octave": 4})

        # Test with invalid note name
        with pytest.raises(ValueError, match="Unrecognized note name"):
            Note.fill_missing_fields({"note_name": "H"})

        # Test MIDI number input
        filled = Note.fill_missing_fields(60)
        assert filled["note_name"] == "C"
        assert filled["octave"] == 4

        # Test invalid MIDI number
        with pytest.raises(ValueError, match="Invalid MIDI number"):
            Note.fill_missing_fields(128)

        # Test string input
        filled = Note.fill_missing_fields("C4")
        assert filled["note_name"] == "C"
        assert filled["octave"] == 4

    def test_note_comparison_methods(self):
        """Test note comparison based on MIDI number"""
        note1 = Note(note_name="C", octave=4)
        note2 = Note(note_name="C", octave=4)
        note3 = Note(note_name="D", octave=4)

        assert note1 == note2
        assert note1 != note3
        assert note1.midi_number < note3.midi_number
        assert note3.midi_number > note1.midi_number

    def test_note_transposition(self):
        note = Note(note_name="C", octave=4)
        
        # Test transpose up
        transposed = note.transpose(2)
        assert transposed.note_name == "D"
        assert transposed.octave == 4

        # Test transpose down
        transposed = note.transpose(-1)
        assert transposed.note_name == "B"
        assert transposed.octave == 3

        # Test octave crossing
        transposed = note.transpose(12)
        assert transposed.note_name == "C"
        assert transposed.octave == 5

    def test_enharmonic_equivalents(self):
        """Test getting enharmonic equivalents of a note"""
        note = Note(note_name="C#", octave=4)
        # Test the actual MIDI number instead since we don't have get_enharmonic_equivalents
        flat_equivalent = Note(note_name="Db", octave=4)
        assert note.midi_number == flat_equivalent.midi_number
        assert note.midi_number == 61

    def test_note_validation_edge_cases(self):
        # Test invalid octave
        with pytest.raises(ValidationError):
            Note(note_name="C", octave=9)

        # Test invalid velocity
        with pytest.raises(ValidationError):
            Note(note_name="C", octave=4, velocity=128)

        # Test invalid duration
        with pytest.raises(ValidationError):
            Note(note_name="C", octave=4, duration=0)

    def test_midi_number_validation(self):
        # Test stored_midi_number validation
        with pytest.raises(ValueError, match="Stored MIDI number 61 does not match calculated value 60"):
            Note(
                note_name="C",
                octave=4,
                stored_midi_number=61  # Wrong MIDI number for C4
            )

        # Test valid stored_midi_number
        note = Note(
            note_name="C",
            octave=4,
            stored_midi_number=60  # Correct MIDI number for C4
        )
        assert note.midi_number == 60

    def test_note_name_parsing(self):
        # Test various note name formats
        assert Note.normalize_note_name("c") == "C"
        assert Note.normalize_note_name("Bb") == "Bb"
        assert Note.normalize_note_name("f#") == "F#"
        
        with pytest.raises(ValueError):
            Note.normalize_note_name("")
        
        with pytest.raises(ValueError):
            Note.normalize_note_name("H")

    def test_note_validation_comprehensive(self):
        """Test comprehensive validation scenarios"""
        # Test invalid note name format
        with pytest.raises(ValueError):
            Note.validate_note_name("")
        with pytest.raises(ValueError):
            Note.validate_note_name("CC")
        
        # Test invalid accidental
        with pytest.raises(ValueError):
            Note.validate_note_name("C##")
            
        # Test note name normalization edge cases
        assert Note.normalize_note_name("c") == "C"
        assert Note.normalize_note_name("Bb") == "Bb"
        
        # Test MIDI number validation
        with pytest.raises(ValueError):
            Note(note_name="C", octave=4, stored_midi_number=128)
        with pytest.raises(ValueError):
            Note(note_name="C", octave=4, stored_midi_number=-1)

    def test_midi_conversion_edge_cases(self):
        """Test edge cases in MIDI number conversion."""
        # Test highest valid note (G8 = MIDI 127)
        note = Note(note_name="G", octave=8)
        assert note.midi_number == 127

        # Test invalid note (A8)
        with pytest.raises(ValueError) as exc_info:
            Note(note_name="A", octave=8)
        assert "exceeds MIDI range" in str(exc_info.value)

        # Test invalid note (G#8)
        with pytest.raises(ValueError) as exc_info:
            Note(note_name="G#", octave=8)
        assert "exceeds MIDI range" in str(exc_info.value)

    def test_note_operations(self):
        """Test various note operations"""
        note = Note(note_name="C", octave=4)
        
        # Test transposition
        transposed = note.transpose(2)
        assert transposed.note_name == "D"
        assert transposed.octave == 4
        
        # Test negative transposition
        transposed = note.transpose(-1)
        assert transposed.note_name == "B"
        assert transposed.octave == 3
        
        # Test octave changes
        transposed = note.transpose(12)
        assert transposed.note_name == "C"
        assert transposed.octave == 5

    def test_note_properties_comprehensive(self):
        """Test comprehensive note properties"""
        note = Note(note_name="C#", octave=4)
        
        # Test full note name
        assert note.full_note_name == "C#4"
        
        # Test MIDI number calculation
        assert note.midi_number == 61
        
        # Test enharmonic equivalents
        assert note.get_enharmonic(prefer_flats=True).note_name == "Db"
        assert note.get_enharmonic(prefer_flats=False).note_name == "C#"

    def test_note_factory_methods(self):
        """Test factory methods comprehensively"""
        # Test from_midi with various parameters
        note = Note.from_midi(60, duration=2.0, position=1.0, velocity=100)
        assert note.duration == 2.0
        assert note.position == 1.0
        assert note.velocity == 100
        
        # Test from_name with various formats
        note = Note.from_name("C#4", duration=1.5)
        assert note.note_name == "C#"
        assert note.octave == 4
        assert note.duration == 1.5
        
        # Test invalid inputs
        with pytest.raises(ValueError):
            Note.from_midi(128)
        with pytest.raises(ValueError):
            Note.from_name("H4")

class TestRhythmNote:
    def test_rhythm_note_creation(self):
        note = RhythmNote(position=0.0, duration=1.0, velocity=64)
        assert note.position == 0.0
        assert note.duration == 1.0
        assert note.velocity == 64
        assert note.accent is False
        assert note.tuplet_ratio == (1, 1)

    def test_rhythm_note_validation(self):
        with pytest.raises(ValidationError):
            RhythmNote(position=-1.0)
        with pytest.raises(ValidationError):
            RhythmNote(duration=0.0)
        with pytest.raises(ValidationError):
            RhythmNote(velocity=128)

    def test_tuplet_ratio_validation(self):
        note = RhythmNote(tuplet_ratio=(3, 2))
        assert note.tuplet_ratio == (3, 2)
        
        with pytest.raises(ValidationError):
            RhythmNote(tuplet_ratio=(0, 1))
        with pytest.raises(ValidationError):
            RhythmNote(tuplet_ratio=(1, 0))

    def test_actual_duration(self):
        note = RhythmNote(duration=1.0, tuplet_ratio=(3, 2))
        assert note.actual_duration == 1.0 * 2/3

    def test_actual_position(self):
        note = RhythmNote(position=1.0, tuplet_ratio=(3, 2))
        assert note.actual_position == 1.0 * 2/3

    def test_actual_velocity(self):
        note = RhythmNote(velocity=64, accent=True)
        assert note.actual_velocity > 64

    def test_rhythm_note_edge_cases(self):
        """Test edge cases for rhythm note validation."""
        with pytest.raises(ValidationError) as exc_info:
            RhythmNote(position=-1.0)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            RhythmNote(duration=0)
        assert "Input should be greater than 0" in str(exc_info.value)

    def test_rhythm_note_properties(self):
        """Test RhythmNote property calculations."""
        note = RhythmNote(
            position=1.0,
            duration=1.0,
            velocity=64,
            accent=True,
            groove_offset=0.1,
            groove_velocity=1.5
        )

        # Test actual_velocity with accent and groove
        assert note.actual_velocity == min(127, round(64 * 1.2 * 1.5))

        # Test position with groove offset
        assert note.actual_position == 1.1  # 1.0 + (0.1 * 1.0)

        # Test actual_duration
        assert note.actual_duration == 1.0  # No tuplet ratio modification

    def test_rhythm_note_comparison(self):
        """Test RhythmNote comparison methods."""
        note1 = RhythmNote(position=1.0, duration=1.0)
        note2 = RhythmNote(position=1.0, duration=1.0)
        note3 = RhythmNote(position=2.0, duration=1.0)

        # Test equality
        assert note1 == note2
        assert not note1 == note3

        # Test dictionary comparison
        note_dict = {
            "position": 1.0,
            "duration": 1.0,
            "velocity": 64,
            "accent": False,
            "tuplet_ratio": (1, 1),
            "groove_offset": 0.0,
            "groove_velocity": 1.0
        }
        assert note1 == note_dict

    def test_note_additional_methods(self):
        """Test additional methods for Note class"""
        # Create test notes
        c4 = Note(note_name="C", octave=4)  # MIDI 60
        d4 = Note(note_name="D", octave=4)  # MIDI 62

        # Debug prints
        print(f"\nC4 MIDI number: {c4.midi_number}")
        print(f"D4 MIDI number: {d4.midi_number}")

        # Test basic equality
        assert c4 != d4, "C4 should not equal D4"
        
        # Test less than
        try:
            result = c4 < d4
            assert result, "C4 should be less than D4"
        except TypeError as e:
            pytest.fail(f"Comparison failed: {e}")

        # Test greater than
        assert d4 > c4, "D4 should be greater than C4"

        # Test string representation
        assert str(c4) == "C4", "String representation should be 'C4'"
        assert c4.full_note_name == "C4", "full_note_name should be 'C4'"

        # Test hash functionality
        note_set = {c4, d4}
        assert len(note_set) == 2, "Set should contain two distinct notes"

    def test_rhythm_note_additional_methods(self):
        """Test additional RhythmNote methods and properties"""
        note = RhythmNote(
            position=1.0,
            duration=2.0,
            velocity=80,
            accent=True,
            tuplet_ratio=(3, 2),
            groove_offset=0.1,
            groove_velocity=1.1
        )
        
        # Test actual duration calculation
        assert note.actual_duration == pytest.approx(2.0 * (2/3))
        
        # Test actual position calculation
        expected_pos = (1.0 * (2/3)) + (0.1 * 2.0)
        assert note.actual_position == pytest.approx(expected_pos)
        
        # Test actual velocity calculation
        assert note.actual_velocity == min(127, round(80 * 1.2 * 1.1))
    @field_validator("octave")
    @classmethod
    def validate_octave(cls, v: int) -> int:
        """Validate octave is within valid range."""
        if not 0 <= v <= 8:
            raise ValueError("Octave must be between 0 and 8")  # Modified error message
        return v
