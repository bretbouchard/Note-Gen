"""Tests for the Chord class."""
import pytest
from models.note import Note
from models.chord import Chord

def test_chord_creation() -> None:
    """Test basic chord creation."""
    # Test major chord
    chord = Chord(root=Note.from_str("C"))
    assert chord.root.name == "C"
    assert chord.quality == "major"
    assert chord.inversion == 0
    assert len(chord.notes) == 4  # Root + 3 notes
    assert [note.note_name for note in chord.notes] == ["C", "E", "G", "C"]

    # Test minor chord
    chord = Chord(root=Note.from_str("A"), quality="minor")
    assert chord.root.name == "A"
    assert chord.quality == "minor"
    assert [note.note_name for note in chord.notes] == ["A", "C", "E", "A"]

def test_chord_inversions() -> None:
    """Test chord inversions."""
    # First inversion of C major
    chord = Chord(root=Note.from_str("C"), inversion=1)
    notes = [note.note_name for note in chord.notes]
    assert notes == ["E", "G", "C", "E"]

    # Second inversion
    chord = Chord(root=Note.from_str("C"), inversion=2)
    notes = [note.note_name for note in chord.notes]
    assert notes == ["G", "C", "E", "G"]

def test_seventh_chords() -> None:
    """Test seventh chord creation."""
    # Major 7th
    chord = Chord(root=Note.from_str("C"), quality="major7")
    notes = [note.note_name for note in chord.notes]
    assert notes == ["C", "E", "G", "B", "C"]

    # Dominant 7th
    chord = Chord(root=Note.from_str("G"), quality="dominant7")
    notes = [note.note_name for note in chord.notes]
    assert notes == ["G", "B", "D", "F", "G"]

def test_invalid_chord() -> None:
    """Test invalid chord creation."""
    with pytest.raises(ValueError, match="Unknown chord quality"):
        Chord(root=Note.from_str("C"), quality="invalid")

def test_chord_with_note_object() -> None:
    """Test chord creation with Note object."""
    note = Note(name="D", accidental="#", octave=4)
    chord = Chord(root=note)
    assert chord.root.note_name == "D#"
    assert [n.note_name for n in chord.notes] == ["D#", "G", "A#", "D#"]

def test_chord_dict_representation() -> None:
    """Test dictionary representation of chord."""
    chord = Chord(root=Note.from_str("C"))
    chord_dict = chord.dict()
    assert chord_dict["root"]["name"] == "C"
    assert chord_dict["quality"] == "major"
    assert len(chord_dict["chord_notes"]) == 4

def test_complex_chords() -> None:
    """Test complex chord types including diminished, augmented, and extended chords."""
    test_cases = [
        # Diminished variations
        ("C", "diminished", ["C", "Eb", "Gb", "C"]),
        ("C", "diminished7", ["C", "Eb", "Gb", "A", "C"]),
        ("F#", "diminished7", ["F#", "A", "C", "Eb", "F#"]),
        ("G", "half-diminished7", ["G", "Bb", "Db", "F", "G"]),
        
        # Augmented variations
        ("C", "augmented", ["C", "E", "G#", "C"]),
        ("C", "augmented7", ["C", "E", "G#", "Bb", "C"]),
        ("F#", "augmented", ["F#", "A#", "D", "F#"]),
        
        # Extended chords
        ("C", "major9", ["C", "E", "G", "B", "D", "C"]),
        ("C", "minor9", ["C", "Eb", "G", "Bb", "D", "C"]),
        ("C", "dominant9", ["C", "E", "G", "Bb", "D", "C"]),
        ("C", "major11", ["C", "E", "G", "B", "D", "F", "C"]),
        ("F#", "major9", ["F#", "A#", "C#", "E#", "G#", "F#"]),
        
        # Added tone chords
        ("C", "add9", ["C", "E", "G", "D", "C"]),
        ("C", "major6", ["C", "E", "G", "A", "C"]),
        ("C", "minor6", ["C", "Eb", "G", "A", "C"]),
        
        # Sus chords
        ("C", "sus2", ["C", "D", "G", "C"]),
        ("C", "sus4", ["C", "F", "G", "C"]),
        ("C", "7sus4", ["C", "F", "G", "Bb", "C"]),
        
        # Other variations
        ("C", "major-minor7", ["C", "Eb", "G", "B", "C"]),
        ("F#", "major-minor7", ["F#", "A", "C#", "E#", "F#"]),
    ]
    
    for root, quality, expected in test_cases:
        chord = Chord(root=Note.from_str(root), quality=quality)
        notes = [note.note_name for note in chord.notes]
        assert notes == expected, f"Failed for {root} {quality} chord"

def test_diminished_chords() -> None:
    """Test diminished chord variations."""
    test_cases = [
        # Basic diminished triad
        ("C", "diminished", ["C", "Eb", "Gb", "C"]),
        ("F#", "diminished", ["F#", "A", "C", "F#"]),
        ("Bb", "diminished", ["Bb", "Db", "E", "Bb"]),
        
        # Diminished seventh
        ("C", "diminished7", ["C", "Eb", "Gb", "A", "C"]),
        ("F#", "diminished7", ["F#", "A", "C", "Eb", "F#"]),
        ("Bb", "diminished7", ["Bb", "Db", "E", "G", "Bb"]),
        
        # Half-diminished seventh (minor 7 flat 5)
        ("C", "half-diminished7", ["C", "Eb", "Gb", "Bb", "C"]),
        ("F#", "half-diminished7", ["F#", "A", "C", "E", "F#"]),
        ("Bb", "half-diminished7", ["Bb", "Db", "E", "Ab", "Bb"]),
    ]
    
    for root, quality, expected in test_cases:
        chord = Chord(root=Note.from_str(root), quality=quality)
        notes = [note.note_name for note in chord.notes]
        assert notes == expected, f"Failed for {root} {quality} chord"

def test_augmented_chord() -> None:
    """Test augmented chord variations."""
    test_cases = [
        # Basic augmented triad
        ("C", "augmented", ["C", "E", "G#", "C"]),
        ("F#", "augmented", ["F#", "A#", "D", "F#"]),
        ("Bb", "augmented", ["Bb", "D", "F#", "Bb"]),
        
        # Augmented seventh (augmented triad with minor seventh)
        ("C", "augmented7", ["C", "E", "G#", "Bb", "C"]),
        ("F#", "augmented7", ["F#", "A#", "D", "E", "F#"]),
        ("Bb", "augmented7", ["Bb", "D", "F#", "Ab", "Bb"]),
    ]
    
    for root, quality, expected in test_cases:
        chord = Chord(root=Note.from_str(root), quality=quality)
        notes = [note.note_name for note in chord.notes]
        assert notes == expected, f"Failed for {root} {quality} chord"

def test_extended_chords() -> None:
    """Test extended chord creation."""
    test_cases = [
        # 9th chords
        ("C", "major9", ["C", "E", "G", "B", "D", "C"]),
        ("C", "minor9", ["C", "Eb", "G", "Bb", "D", "C"]),
        ("C", "dominant9", ["C", "E", "G", "Bb", "D", "C"]),

        # 11th chords
        ("C", "major11", ["C", "E", "G", "B", "D", "F", "C"]),
        ("C", "minor11", ["C", "Eb", "G", "Bb", "D", "F", "C"]),

        # Added tone chords
        ("C", "major6", ["C", "E", "G", "A", "C"]),
        ("C", "minor6", ["C", "Eb", "G", "A", "C"]),
        ("C", "add9", ["C", "E", "G", "D", "C"]),
        ("C", "minor-add9", ["C", "Eb", "G", "D", "C"]),

        # Sus chords
        ("C", "sus2", ["C", "D", "G", "C"]),
        ("C", "sus4", ["C", "F", "G", "C"]),
        ("C", "7sus4", ["C", "F", "G", "Bb", "C"]),

        # Test with different roots
        ("F#", "major9", ["F#", "A#", "C#", "E#", "G#", "F#"]),
        ("Bb", "minor9", ["Bb", "Db", "F", "Ab", "C", "Bb"]),
        ("D", "sus4", ["D", "G", "A", "D"]),
        ("G", "major6", ["G", "B", "D", "E", "G"]),
    ]

    for root, quality, expected in test_cases:
        chord = Chord(root=Note.from_str(root), quality=quality)
        notes = [note.note_name for note in chord.notes]
        assert notes == expected, f"Failed for {root} {quality} chord"

def test_chord_types() -> None:
    """Test all chord types with different roots."""
    test_cases = [
        # Basic triads
        ("C", "major", ["C", "E", "G", "C"]),
        ("C", "minor", ["C", "Eb", "G", "C"]),
        ("C", "diminished", ["C", "Eb", "Gb", "C"]),
        ("C", "augmented", ["C", "E", "G#", "C"]),
        
        # Seventh chords
        ("C", "major7", ["C", "E", "G", "B", "C"]),
        ("C", "minor7", ["C", "Eb", "G", "Bb", "C"]),
        ("C", "dominant7", ["C", "E", "G", "Bb", "C"]),
        ("C", "diminished7", ["C", "Eb", "Gb", "A", "C"]),
        ("C", "half-diminished7", ["C", "Eb", "Gb", "Bb", "C"]),
        ("C", "augmented7", ["C", "E", "G#", "Bb", "C"]),
        ("C", "major-minor7", ["C", "Eb", "G", "B", "C"]),
        
        # Test with different roots and accidentals
        ("F#", "major", ["F#", "A#", "C#", "F#"]),
        ("Bb", "minor", ["Bb", "Db", "F", "Bb"]),
        ("D", "augmented", ["D", "F#", "A#", "D"]),
        ("G", "diminished7", ["G", "Bb", "Db", "E", "G"]),
    ]

    for root, quality, expected in test_cases:
        chord = Chord(root=Note.from_str(root), quality=quality)
        notes = [note.note_name for note in chord.notes]
        assert notes == expected, f"Failed for {root} {quality} chord"
