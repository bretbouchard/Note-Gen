"""Tests for the Note class."""
import pytest
from models.note import Note

def test_note_creation() -> None:
    """Test basic note creation."""
    note = Note(name="C")
    assert note.name == "C"
    assert note.accidental == ""
    assert note.octave == 4
    assert note.note_name == "C"
    assert note.duration == 1.0
    assert note.velocity == 64

def test_note_validation() -> None:
    """Test note validation."""
    # Invalid note name
    with pytest.raises(ValueError, match="Invalid note name"):
        Note(name="H")

    # Invalid accidental
    with pytest.raises(ValueError, match="Invalid accidental"):
        Note(name="C", accidental="x")

    # Invalid octave
    with pytest.raises(ValueError, match="Octave must be between -2 and 8"):
        Note(name="C", octave=9)

    # Invalid duration
    with pytest.raises(ValueError, match="Note duration must be greater than zero"):
        Note(name="C", duration=0)

    # Invalid velocity
    with pytest.raises(ValueError, match="Note velocity must be between 0 and 127"):
        Note(name="C", velocity=128)

def test_from_str() -> None:
    """Test note creation from string."""
    # Test natural notes
    assert str(Note.from_str("C")) == "C4"
    assert str(Note.from_str("C4")) == "C4"

    # Test accidentals
    assert str(Note.from_str("C#")) == "C#4"
    assert str(Note.from_str("Cb")) == "Cb4"
    assert str(Note.from_str("C#4")) == "C#4"

    # Test invalid strings
    with pytest.raises(ValueError, match="Empty note string"):
        Note.from_str("")
    with pytest.raises(ValueError, match="Invalid octave"):
        Note.from_str("Cx")

def test_from_midi() -> None:
    """Test note creation from MIDI number."""
    # Test natural notes
    assert str(Note.from_midi(60)) == "C4"  # Middle C
    assert str(Note.from_midi(69)) == "A4"  # A440

    # Test accidentals
    assert str(Note.from_midi(61)) == "C#4"
    assert str(Note.from_midi(70)) == "A#4"

    # Test invalid MIDI numbers
    with pytest.raises(ValueError, match="MIDI number must be between 0 and 127"):
        Note.from_midi(-1)
    with pytest.raises(ValueError, match="MIDI number must be between 0 and 127"):
        Note.from_midi(128)

def test_to_midi() -> None:
    """Test conversion to MIDI number."""
    # Test natural notes
    assert Note(name="C", octave=4).to_midi() == 60  # Middle C
    assert Note(name="A", octave=4).to_midi() == 69  # A440

    # Test accidentals
    assert Note(name="C", accidental="#", octave=4).to_midi() == 61
    assert Note(name="D", accidental="b", octave=4).to_midi() == 61

def test_transpose() -> None:
    """Test note transposition."""
    note = Note(name="C", octave=4)  # Middle C

    # Test upward transposition
    assert str(note.transpose(2)) == "D4"
    assert str(note.transpose(12)) == "C5"

    # Test downward transposition
    assert str(note.transpose(-1)) == "B3"
    assert str(note.transpose(-12)) == "C3"

    # Test invalid transposition
    with pytest.raises(ValueError, match="Transposition would result in invalid MIDI number"):
        note.transpose(-61)  # Too low
    with pytest.raises(ValueError, match="Transposition would result in invalid MIDI number"):
        note.transpose(68)   # Too high

def test_enharmonic() -> None:
    """Test enharmonic equivalents."""
    # Test basic enharmonics
    c_sharp = Note(name="C", accidental="#", octave=4)
    d_flat = Note(name="D", accidental="b", octave=4)
    assert c_sharp.is_enharmonic(d_flat)
    assert str(c_sharp.enharmonic()) == "Db4"

    # Test natural notes
    c = Note(name="C", octave=4)
    assert str(c.enharmonic()) == "C4"  # No enharmonic equivalent

def test_equality() -> None:
    """Test note equality."""
    # Same notes
    assert Note(name="C", octave=4) == Note(name="C", octave=4)

    # Enharmonic equivalents
    assert Note(name="C", accidental="#", octave=4) == Note(name="D", accidental="b", octave=4)

    # Different notes
    assert Note(name="C", octave=4) != Note(name="D", octave=4)

def test_dict_representation() -> None:
    """Test dictionary representation of a Note object."""
    note = Note(name="C", accidental="#", octave=4)
    d = note.model_dump()
    assert d["name"] == "C"
    assert d["accidental"] == "#"
    assert d["octave"] == 4
    assert d["midi_note"] == 61
    assert d["note_name"] == "C#"
    assert d["duration"] == 1.0
    assert d["velocity"] == 64

def test_from_name() -> None:
    """Test note creation from name string."""
    # Test natural notes
    note = Note.from_name("C4")
    assert note.name == "C"
    assert note.accidental == ""
    assert note.octave == 4

    # Test with accidentals
    note = Note.from_name("C#4")
    assert note.name == "C"
    assert note.accidental == "#"
    assert note.octave == 4

    note = Note.from_name("Bb3")
    assert note.name == "B"
    assert note.accidental == "b"
    assert note.octave == 3

    # Test default octave
    note = Note.from_name("C#")
    assert note.name == "C"
    assert note.accidental == "#"
    assert note.octave == 4

    # Test invalid inputs
    with pytest.raises(ValueError):
        Note.from_name("H4")  # Invalid note name
    with pytest.raises(ValueError):
        Note.from_name("Cx4")  # Invalid accidental
    with pytest.raises(ValueError):
        Note.from_name("C4x")  # Invalid octave format
