"""Tests for the Scale class."""
import pytest
from models.note import Note
from models.scale import Scale

def test_scale_creation() -> None:
    """Test basic scale creation."""
    # Test major scale
    scale = Scale(root=Note.from_str("C"), quality="major")
    assert scale.root.name == "C"
    assert scale.quality == "major"
    assert len(scale.notes) == 8  # Root + 7 notes
    assert [note.note_name for note in scale.notes] == ["C", "D", "E", "F", "G", "A", "B", "C"]

    # Test minor scale
    scale = Scale(root=Note.from_str("A"), quality="minor")
    assert scale.root.name == "A"
    assert scale.quality == "minor"
    assert [note.note_name for note in scale.notes] == ["A", "B", "C", "D", "E", "F", "G", "A"]

def test_scale_with_accidentals() -> None:
    """Test scale creation with accidentals."""
    test_cases = [
        # Major scales with sharps
        ("F#", "major", ["F#", "G#", "A#", "B", "C#", "D#", "E#", "F#"]),
        ("C#", "major", ["C#", "D#", "E#", "F#", "G#", "A#", "B#", "C#"]),
        ("G#", "major", ["G#", "A#", "B#", "C#", "D#", "E#", "F##", "G#"]),

        # Major scales with flats
        ("Bb", "major", ["Bb", "C", "D", "Eb", "F", "G", "A", "Bb"]),
        ("Eb", "major", ["Eb", "F", "G", "Ab", "Bb", "C", "D", "Eb"]),
        ("Ab", "major", ["Ab", "Bb", "C", "Db", "Eb", "F", "G", "Ab"]),

        # Minor scales with sharps
        ("F#", "minor", ["F#", "G#", "A", "B", "C#", "D", "E", "F#"]),
        ("C#", "minor", ["C#", "D#", "E", "F#", "G#", "A", "B", "C#"]),
        
        # Minor scales with flats
        ("Bb", "minor", ["Bb", "C", "Db", "Eb", "F", "Gb", "Ab", "Bb"]),
        ("Eb", "minor", ["Eb", "F", "Gb", "Ab", "Bb", "Cb", "Db", "Eb"]),
    ]

    for root, quality, expected in test_cases:
        scale = Scale(root=Note.from_str(root), quality=quality)
        notes = [note.note_name for note in scale.notes]
        assert notes == expected, f"Failed for {root} {quality} scale"

def test_harmonic_minor_scale() -> None:
    """Test harmonic minor scale creation."""
    test_cases = [
        ("A", ["A", "B", "C", "D", "E", "F", "G#", "A"]),
        ("E", ["E", "F#", "G", "A", "B", "C", "D#", "E"]),
        ("B", ["B", "C#", "D", "E", "F#", "G", "A#", "B"]),
        ("F#", ["F#", "G#", "A", "B", "C#", "D", "E#", "F#"]),
        ("C#", ["C#", "D#", "E", "F#", "G#", "A", "B#", "C#"]),
        ("G#", ["G#", "A#", "B", "C#", "D#", "E", "F##", "G#"]),
        
        # Flat keys
        ("D", ["D", "E", "F", "G", "A", "Bb", "C#", "D"]),
        ("G", ["G", "A", "Bb", "C", "D", "Eb", "F#", "G"]),
        ("C", ["C", "D", "Eb", "F", "G", "Ab", "B", "C"]),
        ("F", ["F", "G", "Ab", "Bb", "C", "Db", "E", "F"]),
        ("Bb", ["Bb", "C", "Db", "Eb", "F", "Gb", "A", "Bb"]),
        ("Eb", ["Eb", "F", "Gb", "Ab", "Bb", "Cb", "D", "Eb"]),
    ]

    for root, expected in test_cases:
        scale = Scale(root=Note.from_str(root), quality="harmonic_minor")
        notes = [note.note_name for note in scale.notes]
        assert notes == expected, f"Failed for {root} harmonic minor scale"

def test_melodic_minor_scale() -> None:
    """Test melodic minor scale creation."""
    test_cases = [
        ("A", ["A", "B", "C", "D", "E", "F#", "G#", "A"]),
        ("E", ["E", "F#", "G", "A", "B", "C#", "D#", "E"]),
        ("B", ["B", "C#", "D", "E", "F#", "G#", "A#", "B"]),
        ("F#", ["F#", "G#", "A", "B", "C#", "D#", "E#", "F#"]),
        
        # Flat keys
        ("D", ["D", "E", "F", "G", "A", "B", "C#", "D"]),
        ("G", ["G", "A", "Bb", "C", "D", "E", "F#", "G"]),
        ("C", ["C", "D", "Eb", "F", "G", "A", "B", "C"]),
        ("F", ["F", "G", "Ab", "Bb", "C", "D", "E", "F"]),
        ("Bb", ["Bb", "C", "Db", "Eb", "F", "G", "A", "Bb"]),
    ]

    for root, expected in test_cases:
        scale = Scale(root=Note.from_str(root), quality="melodic_minor")
        notes = [note.note_name for note in scale.notes]
        assert notes == expected, f"Failed for {root} melodic minor scale"

def test_invalid_scale() -> None:
    """Test invalid scale creation."""
    with pytest.raises(ValueError, match="Unknown scale quality"):
        Scale(root=Note.from_str("C"), quality="invalid")

def test_scale_dict_representation() -> None:
    """Test dictionary representation of scale."""
    scale = Scale(root=Note.from_str("C"))
    scale_dict = scale.dict()
    assert scale_dict["root"]["name"] == "C"
    assert scale_dict["quality"] == "major"
    assert len(scale_dict["scale_notes"]) == 8  # Root + 7 notes

def test_scale_types() -> None:
    """Test all scale types with different roots."""
    test_cases = [
        # Major and minor scales
        ("C", "major", ["C", "D", "E", "F", "G", "A", "B", "C"]),
        ("C", "minor", ["C", "D", "Eb", "F", "G", "Ab", "Bb", "C"]),
        ("C", "harmonic_minor", ["C", "D", "Eb", "F", "G", "Ab", "B", "C"]),
        ("C", "melodic_minor", ["C", "D", "Eb", "F", "G", "A", "B", "C"]),
        
        # Modes
        ("C", "dorian", ["C", "D", "Eb", "F", "G", "A", "Bb", "C"]),
        ("C", "phrygian", ["C", "Db", "Eb", "F", "G", "Ab", "Bb", "C"]),
        ("C", "lydian", ["C", "D", "E", "F#", "G", "A", "B", "C"]),
        ("C", "mixolydian", ["C", "D", "E", "F", "G", "A", "Bb", "C"]),
        ("C", "locrian", ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb", "C"]),
        
        # Other scales
        ("C", "whole_tone", ["C", "D", "E", "F#", "G#", "A#", "C"]),
        ("C", "diminished", ["C", "D", "Eb", "F", "Gb", "Ab", "A", "B", "C"]),
        ("C", "augmented", ["C", "D#", "E", "G", "Ab", "B", "C"]),
        ("C", "chromatic", ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C"]),
    ]

    for root, quality, expected in test_cases:
        scale = Scale(root=Note.from_str(root), quality=quality)
        notes = [note.note_name for note in scale.notes]
        assert notes == expected, f"Failed for {root} {quality} scale"
