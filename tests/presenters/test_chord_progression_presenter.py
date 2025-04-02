"""Tests for the chord progression presenter."""


from note_gen.presenters.chord_progression_presenter import ChordProgressionPresenter
from note_gen.models.chord_progression import ChordProgression
from note_gen.models.chord import Chord
from note_gen.core.enums import ChordQuality, ScaleType


def test_present():
    """Test presenting a single chord progression."""
    # Arrange
    progression = ChordProgression(

        name="Test Progression",
        key="C",
        scale_type=ScaleType.MAJOR,
        chords=[
            Chord(root="C", quality=ChordQuality.MAJOR, duration=1),
            Chord(root="F", quality=ChordQuality.MAJOR, duration=1),
        ]
    )

    # Act
    result = ChordProgressionPresenter.present(progression)

    # Assert
    assert "id" in result
    assert result["name"] == progression.name
    assert result["key"] == progression.key
    assert result["scale_type"] == progression.scale_type
    assert len(result["chords"]) == 2
    assert result["chords"][0]["root"] == "C"
    assert result["chords"][0]["quality"] == ChordQuality.MAJOR
    assert result["chords"][0]["duration"] == 1
    assert result["chords"][0]["position"] is None


def test_present_without_id():
    """Test presenting a chord progression without an ID."""
    # Arrange
    progression = ChordProgression(
        name="Test Progression",
        key="C",
        scale_type=ScaleType.MAJOR,
        chords=[
            Chord(root="C", quality=ChordQuality.MAJOR, duration=1),
        ]
    )

    # Act
    result = ChordProgressionPresenter.present(progression)

    # Assert
    assert "id" in result
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

            name="Test Progression 1",
            key="C",
            scale_type=ScaleType.MAJOR,
            chords=[Chord(root="C", quality=ChordQuality.MAJOR, duration=1)]
        ),
        ChordProgression(

            name="Test Progression 2",
            key="D",
            scale_type=ScaleType.MINOR,
            chords=[Chord(root="D", quality=ChordQuality.MINOR, duration=1)]
        )
    ]

    # Act
    result = ChordProgressionPresenter.present_many(progressions)

    # Assert
    assert len(result) == 2
    assert "id" in result[0]
    assert result[0]["name"] == progressions[0].name
    assert "id" in result[1]
    assert result[1]["name"] == progressions[1].name
