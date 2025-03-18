import pytest
import logging
from pydantic import ValidationError
from src.note_gen.models.note import Note

def test_note_initialization() -> None:
    note = Note(note_name="C", octave=4, duration=1, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None)
    assert note.note_name == "C"
    assert note.octave == 4
    assert note.duration == 1
    assert note.velocity == 64
    assert note.stored_midi_number is None

def test_note_midi_computation() -> None:
    note = Note(note_name="C", octave=4, duration=1, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None)
    assert note.midi_number == 60

def test_note_from_name() -> None:
    note = Note.from_name("C#4", duration=1, velocity=64)
    assert note.note_name == "C#"
    assert note.octave == 4

def test_note_from_midi() -> None:
    note = Note.from_midi(60, duration=1, velocity=64)
    assert note.note_name == "C"
    assert note.octave == 4

def test_normalize_note_name() -> None:
    assert Note.normalize_note_name("c") == "C"
    assert Note.normalize_note_name("eb") == "Eb"
    with pytest.raises(ValueError, match="Invalid note name format: empty string"):
        Note.normalize_note_name("")

def test_note_transpose() -> None:
    note = Note.from_name("C4", duration=1, velocity=64)
    transposed_note = note.transpose(2)
    assert transposed_note.note_name == "D"
    assert transposed_note.octave == 4

def test_invalid_note_initialization() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="Z", octave=4, duration=1, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'string_pattern_mismatch'
    assert error['loc'] == ('note_name',)
    assert error['msg'] == "String should match pattern '^[A-G][#b]?$'"

    # Invalid octave (below 0)
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=-1, scale_degree=None, stored_midi_number=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'greater_than_equal'
    assert error['loc'] == ('octave',)
    assert error['msg'] == 'Input should be greater than or equal to 0'
    
    # Invalid octave (above 8)
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=9, scale_degree=None, stored_midi_number=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'less_than_equal'
    assert error['loc'] == ('octave',)
    assert error['msg'] == 'Input should be less than or equal to 8'
    
    # Invalid velocity (below 0)
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=4, velocity=-1, scale_degree=None, stored_midi_number=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'greater_than_equal'
    assert error['loc'] == ('velocity',)
    assert 'Velocity must be between 0 and 127' in error['msg']
    
    # Invalid velocity (above 127)
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=4, velocity=128, scale_degree=None, stored_midi_number=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'less_than_equal'
    assert error['loc'] == ('velocity',)
    assert error['msg'] == 'Input should be less than or equal to 127'
    
    # Invalid duration (negative)
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=4, duration=-1.0, scale_degree=None, stored_midi_number=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'greater_than'
    assert error['loc'] == ('duration',)
    assert error['msg'] == 'Input should be greater than 0'
    
    # Invalid position (negative)
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=4, position=-1.0, scale_degree=None, stored_midi_number=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'greater_than_equal'
    assert error['loc'] == ('position',)
    assert error['msg'] == 'Input should be greater than or equal to 0'

def test_full_note_name() -> None:
    note = Note.from_name("C4", duration=1, velocity=64)
    assert note.full_note_name() == "C4"

def test_midi_conversion() -> None:
    note = Note.from_name("C4", duration=1, velocity=64)
    assert note.midi_number == 60

def test_note_equality() -> None:
    note1 = Note(note_name="C", octave=4, duration=1, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None)
    note2 = Note(note_name="C", octave=4, duration=1, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None)
    assert note1 == note2

def test_invalid_midi_number_initialization() -> None:
    with pytest.raises(ValueError, match="Invalid MIDI number: 128. MIDI number must be between 0 and 127."):
        Note.from_midi(128, duration=1, velocity=64)

def test_transpose_out_of_range_high() -> None:
    note = Note.from_name("C4", duration=1, velocity=64)
    with pytest.raises(ValueError, match="MIDI number out of range"):
        note.transpose(60)  # Enough semitones to exceed octave 8 => error

def test_transpose_out_of_range_low() -> None:
    note = Note.from_name("C4", duration=1, velocity=64)
    with pytest.raises(ValueError, match="MIDI number out of range"):
        note.transpose(-70)

def test_fill_missing_fields_with_dict() -> None:
    data = Note.fill_missing_fields({"note_name": "C", "octave": 4})
    assert data["note_name"] == "C"
    assert data["octave"] == 4
    assert data["duration"] == 1
    assert data["velocity"] == 64
    assert data["stored_midi_number"] is None

def test_fill_missing_fields_none() -> None:
    """Test that fill_missing_fields raises ValueError for None input."""
    with pytest.raises(ValueError) as excinfo:
        # Using type: ignore to suppress mypy error since we're intentionally testing invalid input
        Note.fill_missing_fields(None)  # type: ignore
    
    assert "Input data must be a dictionary, integer, or string" in str(excinfo.value)

def test_fill_missing_fields_with_none() -> None:
    """Test that fill_missing_fields handles None values in dictionary."""
    with pytest.raises(ValueError) as excinfo:
        # Using type: ignore to suppress mypy error since we're intentionally testing invalid input
        Note.fill_missing_fields(None)  # type: ignore

def test_fill_missing_fields_with_invalid_string() -> None:
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.fill_missing_fields("Invalid")

def test_from_full_name() -> None:
    note = Note.from_full_name("G#4", duration=1, velocity=64)
    assert note.note_name == "G#"
    assert note.octave == 4
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.from_full_name("H#4")

def test_fill_missing_fields_with_midi() -> None:
    data = Note.fill_missing_fields(60)
    assert data["stored_midi_number"] == 60
    assert data["octave"] == 4

def test_from_full_name_valid() -> None:
    note = Note.from_full_name("C#4", duration=1, velocity=64)
    assert note.note_name == "C#"
    assert note.octave == 4

def test_from_full_name_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.from_full_name("Invalid")

def test_midi_to_note_octave_valid() -> None:
    note_name, octave = Note._midi_to_note_octave(60)
    assert note_name == "C"
    assert octave == 4

def test_midi_to_note_octave_invalid() -> None:
    with pytest.raises(ValueError, match="MIDI number out of range"):
        Note._midi_to_note_octave(128)

def test_note_octave_to_midi_valid() -> None:
    midi_number = Note._note_octave_to_midi("C", 4)
    assert midi_number == 60

def test_note_octave_to_midi_invalid_note() -> None:
    with pytest.raises(ValueError, match="Unrecognized note name"):
        Note._note_octave_to_midi("Invalid", 4)

def test_note_name_to_midi_valid() -> None:
    midi_offset = Note.note_name_to_midi("C")
    assert midi_offset == 0

def test_note_name_to_midi_invalid() -> None:
    with pytest.raises(ValueError, match="Unrecognized note name"):
        Note.note_name_to_midi("Invalid")

def test_fill_missing_fields_empty() -> None:
    data = Note.fill_missing_fields({})
    assert data == {
        'note_name': 'C',
        'octave': 4,
        'duration': 1.0,
        'position': 0.0,
        'velocity': 64,
        'stored_midi_number': None,
        'scale_degree': None
    }

def test_fill_missing_fields_invalid_type() -> None:
    with pytest.raises(ValueError) as excinfo:
        Note.fill_missing_fields(1.23)

    assert "Input data must be a dictionary, integer, or string" in str(excinfo.value)

def test_midi_to_note_octave_limits() -> None:
    note_name, octave = Note._midi_to_note_octave(0)
    assert note_name == "C"
    assert octave == 0

    note_name, octave = Note._midi_to_note_octave(127)
    assert note_name == "G"
    assert octave == 9

def test_note_octave_to_midi_invalid() -> None:
    with pytest.raises(ValueError, match="Unrecognized note name"):
        Note._note_octave_to_midi("InvalidNote", 4)

def test_transpose_to_limits() -> None:
    note = Note.from_name("C4", duration=1, velocity=64)

    # Transpose to the upper limit of MIDI numbers
    transposed_note = note.transpose(48)  # Valid transposition, should reach MIDI 108
    assert transposed_note.midi_number == 108
    assert transposed_note.octave == 8
    assert transposed_note.note_name == "C"

    # Transpose beyond the valid range should raise an error
    with pytest.raises(ValueError, match="MIDI number out of range"):
        note.transpose(60)  # Transpose too high, exceeds octave 8

def test_normalize_note_name_edge_cases() -> None:
    assert Note.normalize_note_name("c") == "C"
    assert Note.normalize_note_name("eb") == "Eb"
    with pytest.raises(ValueError, match="Invalid note name format: empty string"):
        Note.normalize_note_name("")

def test_fill_missing_fields_invalid_dict() -> None:
    with pytest.raises(ValueError, match="Unrecognized note name"):
        Note.fill_missing_fields({"note_name": "Invalid", "octave": 4})

    with pytest.raises(ValueError) as excinfo:
        Note.fill_missing_fields({"note_name": "C", "octave": 10})
    assert "Invalid note data" in str(excinfo.value)

def test_check_validations_invalid_duration() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=4, duration=0, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None)  # Invalid duration
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'greater_than'
    assert error['loc'] == ('duration',)
    assert error['msg'] == 'Input should be greater than 0'

def test_check_validations_invalid_octave() -> None:
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=9, duration=1, position=0.0, velocity=64, stored_midi_number=None, scale_degree=None)
    
    error = excinfo.value.errors()[0]
    assert error['type'] == 'less_than_equal'
    assert error['loc'] == ('octave',)
    assert error['msg'] == 'Input should be less than or equal to 8'

def test_midi_number_calculation() -> None:
    note = Note(note_name="C", octave=4, duration=1, position=0.0, stored_midi_number=None, velocity=64, scale_degree=None)
    assert note.midi_number == 60  # Check calculated MIDI number

def test_normalize_note_name_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid note name format: empty string"):
        Note.normalize_note_name("")  # Empty name
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.normalize_note_name("123")  # Invalid string

def test_transpose_invalid_octave() -> None:
    note = Note.from_name("C8", duration=1, velocity=64)
    with pytest.raises(ValueError, match="MIDI number out of range"):
        note.transpose(12)  # Enough to push into octave 9 => error

def test_fill_missing_fields_float() -> None:
    with pytest.raises(ValueError) as excinfo:
        # Using type: ignore to suppress mypy error since we're intentionally testing invalid input
        Note.fill_missing_fields(1.5)  # type: ignore
    
    assert "Input data must be a dictionary, integer, or string" in str(excinfo.value)

def test_invalid_note_initialization() -> None:
    # Test invalid velocity
    with pytest.raises(ValidationError) as excinfo:
        Note(note_name="C", octave=4, velocity=-1, scale_degree=None, stored_midi_number=None)

    error = excinfo.value.errors()[0]
    assert error['type'] == 'greater_than_equal'
    assert error['loc'] == ('velocity',)
    assert 'Input should be greater than or equal to 0' in error['msg']
    def test_from_note_name_valid():
        """Test creating Note from valid note names."""
        note = Note.from_note_name("C")
        assert note.note_name == "C"
        assert note.octave == 4  # Default octave
        
        note = Note.from_note_name("F#")
        assert note.note_name == "F#"
        assert note.octave == 4
        
        note = Note.from_note_name("Bb")
        assert note.note_name == "Bb"
        assert note.octave == 4

    def test_from_note_name_invalid():
        """Test creating Note from invalid note names."""
        with pytest.raises(ValueError, match="Invalid note name: H"):
            Note.from_note_name("H")
            
        with pytest.raises(ValueError, match="Invalid note name: C##"):
            Note.from_note_name("C##")
            
        with pytest.raises(ValueError, match="Invalid note name: X"):
            Note.from_note_name("X")

    def test_from_note_name_properties():
        """Test Note properties when created from note name."""
        note = Note.from_note_name("C")
        assert note.midi_number == 60  # C4 = MIDI 60
        assert note.duration == 1
        assert note.position == 0.0
        assert note.velocity == 64
        assert note.stored_midi_number is None
        assert note.scale_degree is None

    def test_from_note_name_immutable():
        """Test that from_note_name creates independent Note instances."""
        note1 = Note.from_note_name("C")
        note2 = Note.from_note_name("C")
        assert note1 is not note2
        assert note1 == note2