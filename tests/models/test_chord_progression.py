import pytest
from unittest.mock import MagicMock
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.enums import ChordQualityType

@pytest.fixture
def setup_chord_progression() -> ChordProgression:
    scale_info = ScaleInfo(root=Note(name='C', octave=4), scale_type='major')  # Provide the required root argument
    chords = [
        Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR),
        Chord(root=Note(name='G', octave=4), quality=ChordQualityType.MAJOR)
    ]
    return ChordProgression(scale_info=scale_info, chords=chords)

def test_initialization_with_valid_data(setup_chord_progression: ChordProgression) -> None:
    assert setup_chord_progression.scale_info is not None
    assert setup_chord_progression.chords is not None  # Ensure chords is not None
    assert len(setup_chord_progression.chords) == 2

def test_initialization_with_empty_chords() -> None:
    """Test case for initializing ChordProgression with empty chords."""
    scale_info = ScaleInfo(root=Note(name='C', octave=4), scale_type='major')  # Ensure scale_info is valid
    with pytest.raises(ValueError, match="Chords cannot be empty."):
        ChordProgression(scale_info=scale_info, chords=[])

def test_empty_chords_in_progression() -> None:
    with pytest.raises(ValueError, match="Chords cannot be empty"):
        ChordProgression(scale_info=ScaleInfo(root=Note(name='C', octave=4)), chords=[])

def test_empty_chords_in_progression_2() -> None:
    with pytest.raises(ValueError, match="Chords cannot be empty"):
        ChordProgression(scale_info=ScaleInfo(root=Note(name='C', octave=4)), chords=[])

def test_add_chord(setup_chord_progression: ChordProgression) -> None:
    new_chord = Chord(root=Note(name='D', octave=4), quality=ChordQualityType.MAJOR)
    setup_chord_progression.add_chord(new_chord)
    assert len(setup_chord_progression.chords) == 3
    assert setup_chord_progression.chords[-1] == new_chord

def test_get_chord_at(setup_chord_progression: ChordProgression, index: int = 0) -> None:
    chord = setup_chord_progression.get_chord_at(index)
    assert chord is not None
    if chord.root is not None:  # Ensure root is not None before accessing its attributes
        assert chord.root.name == 'C'

def test_get_all_chords(setup_chord_progression: ChordProgression) -> list[Chord]:
    all_chords = setup_chord_progression.get_all_chords()
    assert len(all_chords) == 2  # Ensure we have the initial two chords
    return all_chords

def test_transpose(setup_chord_progression: ChordProgression) -> None:
    setup_chord_progression.transpose(2)
    # Add assertions to verify the transposition logic if needed

def test_validate_chords_invalid_type(setup_chord_progression: ChordProgression) -> None:
    with pytest.raises(ValueError, match="1 validation error for ChordProgression"):
        ChordProgression(scale_info=ScaleInfo(root=Note(name='C', octave=4), scale_type='major'), chords=["invalid_chord"])

def test_validate_chords_none(setup_chord_progression: ChordProgression) -> None:
    with pytest.raises(ValueError, match="1 validation error for ChordProgression"):
        ChordProgression(scale_info=ScaleInfo(root=Note(name='C', octave=4), scale_type='major'), chords=None)

def test_validate_scale_info_none() -> None:
    """Test case for validating ScaleInfo when it is None."""
    with pytest.raises(ValueError):
        ChordProgression(scale_info=None, chords=[Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)])])

def test_validate_scale_info_invalid_type() -> None:
    with pytest.raises(ValueError, match="1 validation error for ChordProgression"):
        ChordProgression(scale_info="invalid_scale_info", chords=[Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR)])

def test_invalid_chord_creation() -> None:
    with pytest.raises(ValueError, match="Chord notes cannot be empty"):
        Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[])

def test_valid_chord_creation() -> None:
    chord = Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)])
    assert chord is not None
    assert chord.root.name == 'C'
    assert chord.quality == ChordQualityType.MAJOR

def test_chord_progression_with_invalid_scale_info() -> None:
    with pytest.raises(ValueError):
        ChordProgression(scale_info=None, chords=[Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)])])

def test_chord_progression_length() -> None:
    chords = [Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)]) for _ in range(3)]  # Create 3 valid Chords
    progression = ChordProgression(scale_info=ScaleInfo(root=Note(name='C', octave=4), scale_type='major'), chords=chords)
    assert len(progression.chords) == len(chords)

def test_empty_chords_in_progression_3() -> None:
    with pytest.raises(ValueError, match="Chords cannot be empty"):
        ChordProgression(scale_info=ScaleInfo(root=Note(name='C', octave=4), scale_type='major'), chords=[])

def test_valid_chord_creation_2() -> None:
    chord = Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)])
    assert chord is not None
    assert chord.root.name == 'C'
    assert chord.quality == ChordQualityType.MAJOR

def test_invalid_chord_creation_2() -> None:
    with pytest.raises(ValueError, match="Chord notes cannot be empty"):
        Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[])

def test_chord_progression_with_invalid_scale_info_2() -> None:
    with pytest.raises(ValueError):
        ChordProgression(scale_info=None, chords=[Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)])])

def test_chord_progression_length_2() -> None:
    chords = [Chord(root=Note(name='C', octave=4), quality=ChordQualityType.MAJOR, notes=[Note(name='C', octave=4), Note(name='E', octave=4), Note(name='G', octave=4)]) for _ in range(3)]  # Create 3 valid Chords
    progression = ChordProgression(scale_info=ScaleInfo(root=Note(name='C', octave=4), scale_type='major'), chords=chords)
    assert len(progression.chords) == len(chords)
