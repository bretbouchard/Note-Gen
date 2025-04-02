"""Tests for the chord progression presenter."""
import pytest
from bson import ObjectId

from src.note_gen.presenters.chord_progression_presenter import ChordProgressionPresenter
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord import Chord


def test_present():
    """Test presenting a single chord progression."""
    # Arrange
    progression = ChordProgression(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        name="Test Progression",
        key="C",
        scale_type="MAJOR",
        chords=[
            Chord(root=1, quality="MAJOR", duration=1, position=0),
            Chord(root=4, quality="MAJOR", duration=1, position=1),
        ]
    )

    # Act
    result = ChordProgressionPresenter.present(progression)

    # Assert
    assert result["id"] == str(progression.id)
    assert result["name"] == progression.name
    assert result["key"] == progression.key
    assert result["scale_type"] == progression.scale_type
    assert len(result["chords"]) == 2
    assert result["chords"][0]["root"] == 1
    assert result["chords"][0]["quality"] == "MAJOR"
    assert result["chords"][0]["duration"] == 1
    assert result["chords"][0]["position"] == 0


def test_present_without_id():
    """Test presenting a chord progression without an ID."""
    # Arrange
    progression = ChordProgression(
        name="Test Progression",
        key="C",
        scale_type="MAJOR",
        chords=[
            Chord(root=1, quality="MAJOR", duration=1),
        ]
    )

    # Act
    result = ChordProgressionPresenter.present(progression)

    # Assert
    assert result["id"] is None
    assert result["name"] == progression.name
    assert result["key"] == progression.key
    assert result["scale_type"] == progression.scale_type
    assert len(result["chords"]) == 1
    assert result["chords"][0]["position"] is None


def test_present_many():
    """Test presenting multiple chord progressions."""
    # Arrange
    progressions = [
        ChordProgression(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
            name="Test Progression 1",
            key="C",
            scale_type="MAJOR",
            chords=[Chord(root=1, quality="MAJOR", duration=1)]
        ),
        ChordProgression(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9c"),
            name="Test Progression 2",
            key="D",
            scale_type="MINOR",
            chords=[Chord(root=1, quality="MINOR", duration=1)]
        )
    ]

    # Act
    result = ChordProgressionPresenter.present_many(progressions)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(progressions[0].id)
    assert result[0]["name"] == progressions[0].name
    assert result[1]["id"] == str(progressions[1].id)
    assert result[1]["name"] == progressions[1].name
