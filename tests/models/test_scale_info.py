import pytest
from pydantic import BaseModel, ConfigDict
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType

@pytest.fixture
def c_major_scale():
    return ScaleInfo(
        root=Note(note_name="C", octave=4),
        scale_type=ScaleType.MAJOR,
        key="C"
    )

def test_get_note_for_degree(c_major_scale):
    # Test all degrees in C major scale
    expected_notes = ["C", "D", "E", "F", "G", "A", "B"]
    for degree, expected in enumerate(expected_notes, start=1):
        note = c_major_scale.get_note_for_degree(degree)
        assert note.note_name == expected

def test_get_note_for_degree_minor_scale():
    scale = ScaleInfo(
        root=Note(note_name="A", octave=4),
        scale_type=ScaleType.MINOR,
        key="A"
    )
    # Test all degrees in A minor scale
    expected_notes = ["A", "B", "C", "D", "E", "F", "G"]
    for degree, expected in enumerate(expected_notes, start=1):
        note = scale.get_note_for_degree(degree)
        assert note.note_name == expected

def test_get_note_for_degree_wrapping(c_major_scale):
    # Test degree wrapping (degree > 7)
    note = c_major_scale.get_note_for_degree(8)
    assert note.note_name == "C"
    assert note.octave == 5

def test_get_note_for_degree_negative(c_major_scale):
    # Test negative degrees
    note = c_major_scale.get_note_for_degree(-1)
    assert note.note_name == "B"
    assert note.octave == 3
