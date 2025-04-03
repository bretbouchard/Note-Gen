"""Tests for sequence generation models."""
import pytest
from note_gen.models.sequence_generation import SequenceGeneration
from note_gen.models.note import Note


def test_sequence_generation_init():
    """Test SequenceGeneration initialization."""
    # Create a sequence generation model
    seq_gen = SequenceGeneration()
    
    # Verify it was created
    assert isinstance(seq_gen, SequenceGeneration)


def test_create_note_valid():
    """Test creating a note with valid input."""
    # Create a sequence generation model
    seq_gen = SequenceGeneration()
    
    # Create a note with valid input
    note = seq_gen.create_note("C4")
    
    # Verify the note
    assert isinstance(note, Note)
    assert note.pitch == "C"
    assert note.octave == 4


def test_create_note_with_accidental():
    """Test creating a note with an accidental."""
    # Create a sequence generation model
    seq_gen = SequenceGeneration()
    
    # Create a note with an accidental
    note = seq_gen.create_note("C#4")
    
    # Verify the note
    assert isinstance(note, Note)
    assert note.pitch == "C#"
    assert note.octave == 4


def test_create_note_with_flat():
    """Test creating a note with a flat."""
    # Create a sequence generation model
    seq_gen = SequenceGeneration()
    
    # Create a note with a flat
    note = seq_gen.create_note("Bb3")
    
    # Verify the note
    assert isinstance(note, Note)
    assert note.pitch == "Bb"
    assert note.octave == 3


def test_create_note_invalid_string():
    """Test creating a note with an invalid string."""
    # Create a sequence generation model
    seq_gen = SequenceGeneration()
    
    # Attempt to create a note with an invalid string
    with pytest.raises(ValueError, match="Invalid note string"):
        seq_gen.create_note("")


def test_create_note_invalid_octave():
    """Test creating a note with an invalid octave."""
    # Create a sequence generation model
    seq_gen = SequenceGeneration()
    
    # Attempt to create a note with an invalid octave
    with pytest.raises(ValueError, match="Invalid octave"):
        seq_gen.create_note("Cx")


def test_create_note_with_kwargs():
    """Test creating a note with additional keyword arguments."""
    # Create a sequence generation model
    seq_gen = SequenceGeneration()
    
    # Create a note with additional kwargs
    note = seq_gen.create_note("C4", duration=1.0, velocity=64)
    
    # Verify the note
    assert isinstance(note, Note)
    assert note.pitch == "C"
    assert note.octave == 4
    assert note.duration == 1.0
    assert note.velocity == 64
