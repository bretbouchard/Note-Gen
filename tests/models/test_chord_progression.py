"""Test chord progression model."""

import pytest
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.scale import ScaleInfo


@pytest.fixture
def setup_chord_progression() -> ChordProgression:
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    chords = [
        Chord(root=Note.from_name('C4'), quality=ChordQualityType.MAJOR),
        Chord(root=Note.from_name('F4'), quality=ChordQualityType.MAJOR),
        Chord(root=Note.from_name('G4'), quality=ChordQualityType.MAJOR)
    ]
    return ChordProgression(chords=chords, scale_info=scale_info)


def test_initialization_with_valid_data(setup_chord_progression: ChordProgression) -> None:
    """Test initialization with valid data."""
    assert len(setup_chord_progression.chords) == 3
    assert setup_chord_progression.scale_info is not None


def test_initialization_with_empty_chords() -> None:
    """Test initialization with empty chords list."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=[], scale_info=scale_info)


def test_empty_chords_in_progression() -> None:
    """Test empty chords in progression."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=[], scale_info=scale_info)


def test_empty_chords_in_progression_2() -> None:
    """Test empty chords in progression with None."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=None, scale_info=scale_info)


def test_add_chord(setup_chord_progression: ChordProgression) -> None:
    """Test adding a chord to the progression."""
    new_chord = Chord(root=Note.from_name('A4'), quality=ChordQualityType.MINOR)
    setup_chord_progression.add_chord(new_chord)
    assert len(setup_chord_progression.chords) == 4


def test_get_chord_at(setup_chord_progression: ChordProgression) -> None:
    """Test getting a chord at a specific position."""
    chord = setup_chord_progression.get_chord_at(1)
    assert chord.root.note_name == 'F'


def test_get_all_chords(setup_chord_progression: ChordProgression) -> None:
    """Test getting all chords in the progression."""
    chords = setup_chord_progression.get_all_chords()
    assert len(chords) == 3


def test_transpose(setup_chord_progression: ChordProgression) -> None:
    """Test transposing the chord progression."""
    original_root = setup_chord_progression.chords[0].root.note_name
    setup_chord_progression.transpose(2)  # Transpose up 2 semitones
    new_root = setup_chord_progression.chords[0].root.note_name
    assert new_root != original_root


def test_validate_chords_invalid_type() -> None:
    """Test validation with invalid chord type."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=["not a chord"], scale_info=scale_info)


def test_validate_chords_none() -> None:
    """Test validation with None chords."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=None, scale_info=scale_info)


def test_validate_scale_info_none() -> None:
    """Test validation with None scale info."""
    chords = [Chord(root=Note.from_name('C4'), quality=ChordQualityType.MAJOR)]
    with pytest.raises(ValueError):
        ChordProgression(chords=chords, scale_info=None)


def test_validate_scale_info_invalid_type() -> None:
    """Test validation with invalid scale info type."""
    chords = [Chord(root=Note.from_name('C4'), quality=ChordQualityType.MAJOR)]
    with pytest.raises(ValueError):
        ChordProgression(chords=chords, scale_info="not a scale info")


def test_invalid_chord_creation() -> None:
    """Test creating a chord progression with invalid chord."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=["invalid"], scale_info=scale_info)


def test_valid_chord_creation() -> None:
    """Test creating a valid chord progression."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    chords = [Chord(root=Note.from_name('C4'), quality=ChordQualityType.MAJOR)]
    progression = ChordProgression(chords=chords, scale_info=scale_info)
    assert len(progression.chords) == 1


def test_chord_progression_length() -> None:
    """Test getting the length of a chord progression."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    chords = [
        Chord(root=Note.from_name('C4'), quality=ChordQualityType.MAJOR),
        Chord(root=Note.from_name('F4'), quality=ChordQualityType.MAJOR)
    ]
    progression = ChordProgression(chords=chords, scale_info=scale_info)
    assert len(progression.chords) == 2


def test_empty_chords_in_progression_3() -> None:
    """Test empty chords in progression with empty list."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=[], scale_info=scale_info)


def test_valid_chord_creation_2() -> None:
    """Test creating a valid chord progression with multiple chords."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    chords = [
        Chord(root=Note.from_name('C4'), quality=ChordQualityType.MAJOR),
        Chord(root=Note.from_name('F4'), quality=ChordQualityType.MAJOR),
        Chord(root=Note.from_name('G4'), quality=ChordQualityType.MAJOR)
    ]
    progression = ChordProgression(chords=chords, scale_info=scale_info)
    assert len(progression.chords) == 3


def test_invalid_chord_creation_2() -> None:
    """Test creating a chord progression with invalid chord type."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=[123], scale_info=scale_info)


def test_chord_progression_with_invalid_scale_info_2() -> None:
    """Test creating a chord progression with invalid scale info type."""
    chords = [Chord(root=Note.from_name('C4'), quality=ChordQualityType.MAJOR)]
    with pytest.raises(ValueError):
        ChordProgression(chords=chords, scale_info=123)


def test_chord_progression_length_2() -> None:
    """Test getting the length of a chord progression with no chords."""
    scale_info = ScaleInfo(root=Note.from_name('C4'), scale_type='major')
    with pytest.raises(ValueError):
        ChordProgression(chords=[], scale_info=scale_info)
