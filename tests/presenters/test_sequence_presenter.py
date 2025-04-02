"""Tests for the sequence presenter."""
import pytest
from bson import ObjectId

from src.note_gen.presenters.sequence_presenter import SequencePresenter
from src.note_gen.models.sequence import Sequence
from src.note_gen.models.note_sequence import NoteSequence
from src.note_gen.models.note import Note


def test_present_sequence():
    """Test presenting a single sequence."""
    # Arrange
    sequence = Sequence(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        name="Test Sequence",
        metadata={"key": "value"}
    )

    # Act
    result = SequencePresenter.present_sequence(sequence)

    # Assert
    assert result["id"] == str(sequence.id)
    assert result["name"] == sequence.name
    assert result["metadata"] == sequence.metadata


def test_present_sequence_without_id():
    """Test presenting a sequence without an ID."""
    # Arrange
    sequence = Sequence(
        name="Test Sequence",
        metadata={"key": "value"}
    )

    # Act
    result = SequencePresenter.present_sequence(sequence)

    # Assert
    assert result["id"] is None
    assert result["name"] == sequence.name
    assert result["metadata"] == sequence.metadata


def test_present_note_sequence():
    """Test presenting a note sequence."""
    # Arrange
    notes = [
        Note(note_name="C", octave=4, duration=1, velocity=64, position=0),
        Note(note_name="E", octave=4, duration=1, velocity=64, position=1),
        Note(note_name="G", octave=4, duration=1, velocity=64, position=2)
    ]
    sequence = NoteSequence(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        name="Test Note Sequence",
        notes=notes,
        metadata={"key": "value"}
    )

    # Act
    result = SequencePresenter.present_note_sequence(sequence)

    # Assert
    assert result["id"] == str(sequence.id)
    assert result["name"] == sequence.name
    assert result["metadata"] == sequence.metadata
    assert result["type"] == "note_sequence"
    assert len(result["notes"]) == 3
    assert result["notes"][0]["note_name"] == "C"
    assert result["notes"][0]["octave"] == 4
    assert result["notes"][1]["note_name"] == "E"
    assert result["notes"][2]["note_name"] == "G"


def test_present_many_sequences():
    """Test presenting multiple sequences."""
    # Arrange
    sequences = [
        Sequence(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
            name="Test Sequence 1",
            metadata={"key1": "value1"}
        ),
        Sequence(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9c"),
            name="Test Sequence 2",
            metadata={"key2": "value2"}
        )
    ]

    # Act
    result = SequencePresenter.present_many_sequences(sequences)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(sequences[0].id)
    assert result[0]["name"] == sequences[0].name
    assert result[0]["metadata"] == sequences[0].metadata
    assert result[1]["id"] == str(sequences[1].id)
    assert result[1]["name"] == sequences[1].name
    assert result[1]["metadata"] == sequences[1].metadata


def test_present_many_note_sequences():
    """Test presenting multiple note sequences."""
    # Arrange
    sequences = [
        NoteSequence(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
            name="Test Note Sequence 1",
            notes=[
                Note(note_name="C", octave=4, duration=1, velocity=64, position=0)
            ],
            metadata={"key1": "value1"}
        ),
        NoteSequence(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9c"),
            name="Test Note Sequence 2",
            notes=[
                Note(note_name="D", octave=4, duration=1, velocity=64, position=0)
            ],
            metadata={"key2": "value2"}
        )
    ]

    # Act
    result = SequencePresenter.present_many_note_sequences(sequences)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(sequences[0].id)
    assert result[0]["name"] == sequences[0].name
    assert result[0]["metadata"] == sequences[0].metadata
    assert result[0]["type"] == "note_sequence"
    assert len(result[0]["notes"]) == 1
    assert result[0]["notes"][0]["note_name"] == "C"
    assert result[1]["id"] == str(sequences[1].id)
    assert result[1]["name"] == sequences[1].name
    assert result[1]["metadata"] == sequences[1].metadata
    assert result[1]["type"] == "note_sequence"
    assert len(result[1]["notes"]) == 1
    assert result[1]["notes"][0]["note_name"] == "D"


def test_format_notes():
    """Test formatting notes."""
    # Arrange
    notes = [
        Note(note_name="C", octave=4, duration=1, velocity=64, position=0),
        Note(note_name="E", octave=4, duration=1, velocity=64, position=1),
        Note(note_name="G", octave=4, duration=1, velocity=64, position=2)
    ]

    # Act
    result = SequencePresenter._format_notes(notes)

    # Assert
    assert len(result) == 3
    assert result[0]["note_name"] == "C"
    assert result[0]["octave"] == 4
    assert result[0]["duration"] == 1
    assert result[0]["velocity"] == 64
    assert result[0]["position"] == 0
    assert result[1]["note_name"] == "E"
    assert result[2]["note_name"] == "G"
