"""Test chord model."""

import pytest
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.enums import ChordQualityType


def test_chord_creation() -> None:
    """Test creating a chord."""
    root = Note.from_name('C4')
    chord = Chord(root=root, quality=ChordQualityType.MAJOR)
    assert chord.root.note_name == 'C'
    assert chord.root.octave == 4
    assert len(chord.notes) == 3  # Major triad has 3 notes


def test_chord_validation() -> None:
    """Test chord validation."""
    root = Note.from_name('C4')
    with pytest.raises(ValueError):
        Chord(root=root, quality="invalid")


def test_chord_inversion() -> None:
    """Test chord inversion."""
    root = Note.from_name('C4')
    chord = Chord(root=root, quality=ChordQualityType.MAJOR, inversion=1)
    assert len(chord.notes) == 3
    assert chord.notes[0].note_name == 'E'  # First inversion starts on E


def test_chord_from_base() -> None:
    """Test creating a chord from base note."""
    root = Note.from_name('C4')
    chord = Chord(root=root, quality=ChordQualityType.MAJOR)
    assert chord.root.note_name == 'C'
    assert chord.root.octave == 4
    assert len(chord.notes) == 3


def test_chord_quality_types() -> None:
    """Test different chord quality types."""
    root = Note.from_name('C4')
    qualities = [
        ChordQualityType.MAJOR,
        ChordQualityType.MINOR,
        ChordQualityType.DIMINISHED,
        ChordQualityType.AUGMENTED,
        ChordQualityType.DOMINANT,
        ChordQualityType.MAJOR_7,
        ChordQualityType.MINOR_7
    ]
    for quality in qualities:
        chord = Chord(root=root, quality=quality)
        assert chord.quality.quality_type == quality