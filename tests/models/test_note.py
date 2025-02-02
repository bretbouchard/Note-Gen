import pytest
import logging
from src.note_gen.models.note import Note

def test_note_initialization() -> None:
    note = Note(note_name="C", octave=4, duration=1.0, velocity=64)
    assert note.note_name == "C"
    assert note.octave == 4
    assert note.duration == 1.0
    assert note.velocity == 64
    assert note.stored_midi_number is None

def test_note_midi_computation() -> None:
    note = Note(note_name="C", octave=4, duration=1.0, velocity=64)
    assert note.midi_number == 60

def test_note_from_name() -> None:
    note = Note.from_name("C#4", duration=1.0, velocity=64)
    assert note.note_name == "C#"
    assert note.octave == 4

def test_note_from_midi() -> None:
    note = Note.from_midi(60, duration=1.0, velocity=64)
    assert note.note_name == "C"
    assert note.octave == 4

def test_note_normalization() -> None:
    assert Note.normalize_note_name("c") == "C"
    assert Note.normalize_note_name("eb") == "Eb"
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.normalize_note_name("")

def test_note_transpose() -> None:
    note = Note.from_name("C4", duration=1.0, velocity=64)
    transposed_note = note.transpose(2)
    assert transposed_note.note_name == "D"
    assert transposed_note.octave == 4

def test_invalid_note_initialization() -> None:
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note(note_name="Invalid", octave=4, duration=1.0, velocity=64)
    with pytest.raises(ValueError, match="Invalid octave:"):
        Note(note_name="C", octave=10, duration=1.0, velocity=64)

def test_full_note_name() -> None:
    note = Note.from_name("C4", duration=1.0, velocity=64)
    assert note.full_note_name() == "C4"

def test_midi_conversion() -> None:
    note = Note.from_name("C4", duration=1.0, velocity=64)
    assert note.midi_number == 60

def test_note_equality() -> None:
    note1 = Note(note_name="C", octave=4, duration=1.0, velocity=64)
    note2 = Note(note_name="C", octave=4, duration=1.0, velocity=64)
    assert note1 == note2

def test_invalid_midi_number_initialization() -> None:
    with pytest.raises(ValueError, match="MIDI number out of range:"):
        Note.from_midi(128, duration=1.0, velocity=64)

def test_transpose_out_of_range_high() -> None:
    note = Note.from_name("C4", duration=1.0, velocity=64)
    with pytest.raises(ValueError, match="MIDI number out of range"):
        note.transpose(60)  # Enough semitones to exceed octave 8 => error

def test_transpose_out_of_range_low() -> None:
    note = Note.from_name("C4", duration=1.0, velocity=64)
    with pytest.raises(ValueError, match="MIDI number out of range"):
        note.transpose(-70)

def test_fill_missing_fields_with_dict() -> None:
    data = Note.fill_missing_fields({"note_name": "C", "octave": 4})
    assert data["note_name"] == "C"
    assert data["octave"] == 4
    assert data["duration"] == 1.0
    assert data["velocity"] == 64
    assert data["stored_midi_number"] is None

def test_fill_missing_fields_with_none() -> None:
    with pytest.raises(ValueError, match="Expected a dict, int, or str for Note"):
        Note.fill_missing_fields(None)

def test_fill_missing_fields_with_invalid_string() -> None:
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.fill_missing_fields("Invalid")

def test_from_full_name() -> None:
    note = Note.from_full_name("G#4", duration=1.0, velocity=64)
    assert note.note_name == "G#"
    assert note.octave == 4
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.from_full_name("H#4")

def test_fill_missing_fields_with_midi() -> None:
    data = Note.fill_missing_fields(60)
    assert data["stored_midi_number"] == 60
    assert data["octave"] == 4

def test_from_full_name_valid() -> None:
    note = Note.from_full_name("C#4", duration=1.0, velocity=64)
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
    assert data["note_name"] == "C"
    assert data["octave"] == 4
    assert data["duration"] == 1.0
    assert data["velocity"] == 64

def test_fill_missing_fields_invalid_type() -> None:
    with pytest.raises(ValueError, match="Expected a dict, int, or str for Note"):
        Note.fill_missing_fields(3.14)

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
    note = Note.from_name("C4", duration=1.0, velocity=64)

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
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.normalize_note_name("")

def test_fill_missing_fields_invalid_dict() -> None:
    with pytest.raises(ValueError, match="Unrecognized note name"):
        Note.fill_missing_fields({"note_name": "Invalid", "octave": 4})
    with pytest.raises(ValueError, match="Octave must be between 0 and 8: 10"):
        Note.fill_missing_fields({"note_name": "C", "octave": 10})  # Invalid octave

def test_check_validations_invalid_duration() -> None:
    with pytest.raises(ValueError, match="Input should be greater than 0"):
        Note(note_name="C", octave=4, duration=0, velocity=64)  # Invalid duration

def test_check_validations_invalid_octave() -> None:
    with pytest.raises(ValueError, match="Octave must be between 0 and 8: 9"):
        Note.fill_missing_fields({"note_name": "C", "octave": 9})

def test_midi_number_calculation() -> None:
    note = Note(note_name="C", octave=4, duration=1.0, stored_midi_number=None, velocity=64)
    assert note.midi_number == 60  # Check calculated MIDI number

def test_normalize_note_name_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.normalize_note_name("")  # Empty name
    with pytest.raises(ValueError, match="Invalid note name format:"):
        Note.normalize_note_name("123")  # Invalid string

def test_transpose_invalid_octave() -> None:
    note = Note.from_name("C8", duration=1.0, velocity=64)
    with pytest.raises(ValueError, match="MIDI number out of range"):
        note.transpose(12)  # Enough to push into octave 9 => error