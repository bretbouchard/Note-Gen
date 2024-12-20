import pytest
from src.models.scale import Scale
from src.models.note import Note
from src.models.scale_degree import ScaleDegree


def test_scale_initialization() -> None:
    root = Note(name='C', octave=4)
    scale = Scale(root=root, quality='major')
    assert scale.root == root
    assert scale.quality == 'major'


def test_invalid_scale_quality() -> None:
    root = Note(name='C', octave=4)
    with pytest.raises(ValueError):
        Scale(root=root, quality='invalid_quality')


def test_scale_notes_retrieval() -> None:
    root = Note(name='C', octave=4)
    scale = Scale(root=root, quality='major')
    notes = scale.get_scale_notes()
    assert len(notes) == 7  # Major scale has 7 notes
    assert notes[0].name == 'C'
    assert notes[-1].name == 'B'  # Assuming C major scale


def test_scale_degrees_retrieval() -> None:
    root = Note(name='C', octave=4)
    scale = Scale(root=root, quality='major')
    degrees = scale.get_scale_degrees()
    assert len(degrees) == 7  # Major scale has 7 degrees
    assert degrees[0].scale == 'major'


def test_scale_building_from_intervals() -> None:
    root = Note(name='C', octave=4)
    scale = Scale(root=root, quality='major')
    notes = scale.get_scale_notes()
    assert notes[1].name == 'D'  # Check second note of C major scale
    assert notes[2].name == 'E'  # Check third note of C major scale
