"""Tests for Roman numeral chord notation."""
import pytest
from models.note import Note
from models.chord import Chord
from models.scale import Scale

def test_roman_numeral_equivalence() -> None:
    """Test that different representations of the same degree are equivalent."""
    test_cases = [
        # First degree variations
        ("C", "major", ["i", "I", "1", "one"]),
        # Second degree variations
        ("C", "major", ["ii", "II", "2", "two"]),
        # Third degree variations
        ("C", "major", ["iii", "III", "3", "three"]),
        # Fourth degree variations
        ("C", "major", ["iv", "IV", "4", "four"]),
        # Fifth degree variations
        ("C", "major", ["v", "V", "5", "five"]),
        # Sixth degree variations
        ("C", "major", ["vi", "VI", "6", "six"]),
        # Seventh degree variations
        ("C", "major", ["vii", "VII", "7", "seven"]),
    ]

    for root, scale_quality, numerals in test_cases:
        scale = Scale(root=Note.from_str(root), quality=scale_quality)
        expected_notes = None
        
        # Get the notes for the first representation
        chord = Chord.from_roman_numeral(numerals[0], scale)
        expected_notes = [note.note_name for note in chord.notes]
        
        # Test that all representations give the same notes
        for numeral in numerals[1:]:
            chord = Chord.from_roman_numeral(numeral, scale)
            notes = [note.note_name for note in chord.notes]
            assert notes == expected_notes, f"Failed for {numeral} in {root} {scale_quality}"

def test_roman_numeral_chord_variations() -> None:
    """Test that Roman numerals support chord variations."""
    test_cases = [
        # Major variations
        ("C", "major", "I", "major", ["C", "E", "G", "C"]),
        ("C", "major", "I7", "dominant7", ["C", "E", "G", "Bb", "C"]),
        ("C", "major", "Imaj7", "major7", ["C", "E", "G", "B", "C"]),
        
        # Minor variations
        ("C", "major", "ii", "minor", ["D", "F", "A", "D"]),
        ("C", "major", "ii7", "minor7", ["D", "F", "A", "C", "D"]),
        ("C", "major", "iimin7", "minor7", ["D", "F", "A", "C", "D"]),
        
        # Diminished variations
        ("C", "major", "vii°", "diminished", ["B", "D", "F", "B"]),
        ("C", "major", "vii°7", "diminished7", ["B", "D", "F", "Ab", "B"]),
        ("C", "major", "viiø7", "half-diminished7", ["B", "D", "F", "A", "B"]),
        
        # Augmented variations
        ("C", "major", "I+", "augmented", ["C", "E", "G#", "C"]),
        ("C", "major", "I+7", "augmented7", ["C", "E", "G#", "Bb", "C"]),
        
        # Extended chords
        ("C", "major", "Imaj9", "major9", ["C", "E", "G", "B", "D", "C"]),
        ("C", "major", "V9", "dominant9", ["G", "B", "D", "F", "A", "G"]),
        ("C", "major", "ii11", "minor11", ["D", "F", "A", "C", "E", "G", "D"]),
        
        # Sus chords
        ("C", "major", "Isus4", "sus4", ["C", "F", "G", "C"]),
        ("C", "major", "Isus2", "sus2", ["C", "D", "G", "C"]),
        ("C", "major", "V7sus4", "7sus4", ["G", "C", "D", "F", "G"]),
    ]
    
    for root, scale_quality, numeral, chord_quality, expected in test_cases:
        scale = Scale(root=Note.from_str(root), quality=scale_quality)
        chord = Chord.from_roman_numeral(numeral, scale)
        notes = [note.note_name for note in chord.notes]
        assert notes == expected, f"Failed for {numeral} in {root} {scale_quality}"
        assert chord.quality == chord_quality, f"Wrong quality for {numeral}"

def test_invalid_roman_numerals() -> None:
    """Test that invalid Roman numerals raise appropriate errors."""
    scale = Scale(root=Note.from_str("C"), quality="major")
    
    with pytest.raises(ValueError):
        Chord.from_roman_numeral("viii", scale)  # Invalid degree
    
    with pytest.raises(ValueError):
        Chord.from_roman_numeral("Xmaj7", scale)  # Invalid numeral
    
    with pytest.raises(ValueError):
        Chord.from_roman_numeral("I^", scale)  # Invalid modifier

def test_flattened_roman_numerals() -> None:
    """Test flattened Roman numerals."""
    # Create C major scale
    c_major = Scale(root=Note(name="C"), quality="major")
    
    test_cases = [
        # Flattened third
        ("bIII", "major", ["Eb", "G", "Bb", "Eb"]),
        ("bIII7", "dominant7", ["Eb", "G", "Bb", "Db", "Eb"]),
        
        # Flattened sixth
        ("bVI", "major", ["Ab", "C", "Eb", "Ab"]),
        ("bvi", "minor", ["Ab", "Cb", "Eb", "Ab"]),
        ("bVI7", "dominant7", ["Ab", "C", "Eb", "Gb", "Ab"]),
        
        # Flattened second
        ("bII", "major", ["Db", "F", "Ab", "Db"]),
        ("bii7", "minor7", ["Db", "Fb", "Ab", "Cb", "Db"]),
    ]
    
    for numeral, quality, expected in test_cases:
        chord = Chord.from_roman_numeral(numeral, c_major)
        notes = [note.note_name for note in chord.notes]
        assert notes == expected, f"Failed for {numeral} in C major"
        assert chord.quality == quality, f"Wrong quality for {numeral}"

def test_c_major_ii7_chord() -> None:
    """Test ii7 chord in C major."""
    # Create C major scale
    c_major = Scale(root=Note(name="C"), quality="major")
    
    # Create ii7 chord
    ii7 = Chord.from_roman_numeral("ii7", c_major)
    
    # Expected notes: D F A C
    assert ii7.chord_notes[0].name == "D"  # Root
    assert not ii7.chord_notes[0].accidental  # No accidental
    
    assert ii7.chord_notes[1].name == "F"  # Minor third
    assert not ii7.chord_notes[1].accidental  # No accidental
    
    assert ii7.chord_notes[2].name == "A"  # Fifth
    assert not ii7.chord_notes[2].accidental  # No accidental
    
    assert ii7.chord_notes[3].name == "C"  # Minor seventh
    assert not ii7.chord_notes[3].accidental  # No accidental
    
    # Test the quality
    assert ii7.quality == "minor7"

def test_c_major_V7_chord() -> None:
    """Test V7 chord in C major."""
    # Create C major scale
    c_major = Scale(root=Note(name="C"), quality="major")
    
    # Create V7 chord
    V7 = Chord.from_roman_numeral("V7", c_major)
    
    # Expected notes: G B D F
    assert V7.chord_notes[0].name == "G"  # Root
    assert not V7.chord_notes[0].accidental
    
    assert V7.chord_notes[1].name == "B"  # Major third
    assert not V7.chord_notes[1].accidental
    
    assert V7.chord_notes[2].name == "D"  # Fifth
    assert not V7.chord_notes[2].accidental
    
    assert V7.chord_notes[3].name == "F"  # Minor seventh
    assert not V7.chord_notes[3].accidental
    
    # Test the quality
    assert V7.quality == "dominant7"
