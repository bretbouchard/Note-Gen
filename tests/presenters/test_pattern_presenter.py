"""Tests for the pattern presenter."""
import pytest

from note_gen.presenters.pattern_presenter import PatternPresenter
from note_gen.models.patterns import NotePattern
from note_gen.models.rhythm import RhythmPattern, RhythmNote
from note_gen.models.note import Note
from pydantic import BaseModel


def test_present_note_pattern():
    """Test presenting a single note pattern."""
    # Arrange
    pattern = NotePattern(
        name="Test Pattern",
        pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60),
                Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
        tags=["test", "pattern"]
    )

    # Act
    result = PatternPresenter.present_note_pattern(pattern)

    # Assert
    assert "id" in result
    assert result["name"] == pattern.name

    # Check that pattern is a list of dictionaries
    assert isinstance(result["pattern"], list)
    assert len(result["pattern"]) == len(pattern.pattern)
    assert result["tags"] == pattern.tags
    assert result["type"] == "note"


def test_present_rhythm_pattern():
    """Test presenting a single rhythm pattern."""
    # Arrange
    pattern = RhythmPattern(
        name="Test Rhythm",
        pattern=[RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
    )

    # Act
    result = PatternPresenter.present_rhythm_pattern(pattern)

    # Assert
    assert "id" in result
    assert result["name"] == pattern.name

    # Check that pattern is a list of dictionaries
    assert isinstance(result["pattern"], list)
    assert len(result["pattern"]) == len(pattern.pattern)

    assert result["type"] == "rhythm"


def test_present_pattern_note():
    """Test presenting a pattern (note type)."""
    # Arrange
    pattern = NotePattern(
        name="Test Pattern",
        pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60),
                Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
        tags=["test", "pattern"]
    )

    # Act
    result = PatternPresenter.present_pattern(pattern)

    # Assert
    assert "id" in result
    assert result["name"] == pattern.name
    assert result["type"] == "note"


def test_present_pattern_rhythm():
    """Test presenting a pattern (rhythm type)."""
    # Arrange
    pattern = RhythmPattern(
        name="Test Rhythm",
        pattern=[RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
    )

    # Act
    result = PatternPresenter.present_pattern(pattern)

    # Assert
    assert "id" in result
    assert result["name"] == pattern.name
    assert result["type"] == "rhythm"


def test_present_pattern_unknown_type():
    """Test presenting a pattern with unknown type."""
    # Arrange
    class UnknownPattern(BaseModel):
        name: str = "Unknown"

    pattern = UnknownPattern()

    # Act & Assert
    with pytest.raises(ValueError, match="Unknown pattern type"):
        # Type ignore for testing purposes
        PatternPresenter.present_pattern(pattern)  # type: ignore


def test_present_many_note_patterns():
    """Test presenting multiple note patterns."""
    # Arrange
    patterns = [
        NotePattern(
            name="Test Pattern 1",
            pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60),
                    Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
            tags=["test", "pattern"]
        ),
        NotePattern(
            name="Test Pattern 2",
            pattern=[Note(pitch="E", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=64),
                    Note(pitch="F", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=65)],
            tags=["test", "pattern"]
        )
    ]

    # Act
    result = PatternPresenter.present_many_note_patterns(patterns)

    # Assert
    assert len(result) == 2
    assert "id" in result[0]
    assert result[0]["name"] == patterns[0].name
    assert result[0]["type"] == "note"
    assert "id" in result[1]
    assert result[1]["name"] == patterns[1].name
    assert result[1]["type"] == "note"


def test_present_many_rhythm_patterns():
    """Test presenting multiple rhythm patterns."""
    # Arrange
    patterns = [
        RhythmPattern(
            name="Test Rhythm 1",
            pattern=[RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
        ),
        RhythmPattern(
            name="Test Rhythm 2",
            pattern=[RhythmNote(position=0.0, duration=2.0), RhythmNote(position=2.0, duration=2.0)]
        )
    ]

    # Act
    result = PatternPresenter.present_many_rhythm_patterns(patterns)

    # Assert
    assert len(result) == 2
    assert "id" in result[0]
    assert result[0]["name"] == patterns[0].name
    assert result[0]["type"] == "rhythm"
    assert "id" in result[1]
    assert result[1]["name"] == patterns[1].name
    assert result[1]["type"] == "rhythm"


def test_present_many_patterns_mixed():
    """Test presenting multiple patterns of mixed types."""
    # Arrange
    patterns = [
        NotePattern(
            name="Test Pattern",
            pattern=[Note(pitch="C", octave=4, duration=1.0, velocity=64, position=0.0, stored_midi_number=60),
                    Note(pitch="D", octave=4, duration=1.0, velocity=64, position=1.0, stored_midi_number=62)],
            tags=["test", "pattern"]
        ),
        RhythmPattern(
            name="Test Rhythm",
            pattern=[RhythmNote(position=0.0, duration=1.0), RhythmNote(position=1.0, duration=1.0)]
        )
    ]

    # Act
    result = PatternPresenter.present_many_patterns(patterns)

    # Assert
    assert len(result) == 2
    assert "id" in result[0]
    assert result[0]["name"] == patterns[0].name
    assert result[0]["type"] == "note"
    assert "id" in result[1]
    assert result[1]["name"] == patterns[1].name
    assert result[1]["type"] == "rhythm"
