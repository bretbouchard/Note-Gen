"""Tests for the pattern presenter."""
import pytest
from bson import ObjectId

from src.note_gen.presenters.pattern_presenter import PatternPresenter
from src.note_gen.models.patterns import NotePattern, RhythmPattern


def test_present_note_pattern():
    """Test presenting a single note pattern."""
    # Arrange
    pattern = NotePattern(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        name="Test Pattern",
        description="A test pattern",
        pattern="1 2 3 4",
        tags=["test", "pattern"]
    )

    # Act
    result = PatternPresenter.present_note_pattern(pattern)

    # Assert
    assert result["id"] == str(pattern.id)
    assert result["name"] == pattern.name
    assert result["description"] == pattern.description
    assert result["pattern"] == pattern.pattern
    assert result["tags"] == pattern.tags
    assert result["type"] == "note"


def test_present_rhythm_pattern():
    """Test presenting a single rhythm pattern."""
    # Arrange
    pattern = RhythmPattern(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        name="Test Rhythm",
        description="A test rhythm",
        pattern="q q q q",
        tags=["test", "rhythm"]
    )

    # Act
    result = PatternPresenter.present_rhythm_pattern(pattern)

    # Assert
    assert result["id"] == str(pattern.id)
    assert result["name"] == pattern.name
    assert result["description"] == pattern.description
    assert result["pattern"] == pattern.pattern
    assert result["tags"] == pattern.tags
    assert result["type"] == "rhythm"


def test_present_pattern_note():
    """Test presenting a pattern (note type)."""
    # Arrange
    pattern = NotePattern(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        name="Test Pattern",
        description="A test pattern",
        pattern="1 2 3 4",
        tags=["test", "pattern"]
    )

    # Act
    result = PatternPresenter.present_pattern(pattern)

    # Assert
    assert result["id"] == str(pattern.id)
    assert result["name"] == pattern.name
    assert result["type"] == "note"


def test_present_pattern_rhythm():
    """Test presenting a pattern (rhythm type)."""
    # Arrange
    pattern = RhythmPattern(
        id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
        name="Test Rhythm",
        description="A test rhythm",
        pattern="q q q q",
        tags=["test", "rhythm"]
    )

    # Act
    result = PatternPresenter.present_pattern(pattern)

    # Assert
    assert result["id"] == str(pattern.id)
    assert result["name"] == pattern.name
    assert result["type"] == "rhythm"


def test_present_pattern_unknown_type():
    """Test presenting a pattern with unknown type."""
    # Arrange
    class UnknownPattern:
        pass

    pattern = UnknownPattern()

    # Act & Assert
    with pytest.raises(ValueError, match="Unknown pattern type"):
        PatternPresenter.present_pattern(pattern)


def test_present_many_note_patterns():
    """Test presenting multiple note patterns."""
    # Arrange
    patterns = [
        NotePattern(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
            name="Test Pattern 1",
            description="A test pattern",
            pattern="1 2 3 4",
            tags=["test", "pattern"]
        ),
        NotePattern(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9c"),
            name="Test Pattern 2",
            description="Another test pattern",
            pattern="5 6 7 8",
            tags=["test", "pattern"]
        )
    ]

    # Act
    result = PatternPresenter.present_many_note_patterns(patterns)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(patterns[0].id)
    assert result[0]["name"] == patterns[0].name
    assert result[0]["type"] == "note"
    assert result[1]["id"] == str(patterns[1].id)
    assert result[1]["name"] == patterns[1].name
    assert result[1]["type"] == "note"


def test_present_many_rhythm_patterns():
    """Test presenting multiple rhythm patterns."""
    # Arrange
    patterns = [
        RhythmPattern(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
            name="Test Rhythm 1",
            description="A test rhythm",
            pattern="q q q q",
            tags=["test", "rhythm"]
        ),
        RhythmPattern(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9c"),
            name="Test Rhythm 2",
            description="Another test rhythm",
            pattern="h h",
            tags=["test", "rhythm"]
        )
    ]

    # Act
    result = PatternPresenter.present_many_rhythm_patterns(patterns)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(patterns[0].id)
    assert result[0]["name"] == patterns[0].name
    assert result[0]["type"] == "rhythm"
    assert result[1]["id"] == str(patterns[1].id)
    assert result[1]["name"] == patterns[1].name
    assert result[1]["type"] == "rhythm"


def test_present_many_patterns_mixed():
    """Test presenting multiple patterns of mixed types."""
    # Arrange
    patterns = [
        NotePattern(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9b"),
            name="Test Pattern",
            description="A test pattern",
            pattern="1 2 3 4",
            tags=["test", "pattern"]
        ),
        RhythmPattern(
            id=ObjectId("5f9f1b9b9c9d1b9b9c9d1b9c"),
            name="Test Rhythm",
            description="A test rhythm",
            pattern="q q q q",
            tags=["test", "rhythm"]
        )
    ]

    # Act
    result = PatternPresenter.present_many_patterns(patterns)

    # Assert
    assert len(result) == 2
    assert result[0]["id"] == str(patterns[0].id)
    assert result[0]["name"] == patterns[0].name
    assert result[0]["type"] == "note"
    assert result[1]["id"] == str(patterns[1].id)
    assert result[1]["name"] == patterns[1].name
    assert result[1]["type"] == "rhythm"
