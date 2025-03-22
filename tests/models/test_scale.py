import pytest
from src.note_gen.core.enums import ScaleType
from src.note_gen.models.scale import Scale
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.note import Note

@pytest.mark.parametrize("root_note,scale_type", [
    ("C4", ScaleType.MAJOR),
    ("A3", ScaleType.MINOR),
    ("F#4", ScaleType.MAJOR),
    ("Bb3", ScaleType.MINOR),
    ("G2", ScaleType.DORIAN),
])
def test_scale_creation(root_note: str, scale_type: ScaleType):
    scale = Scale(
        root=Note(note_name=root_note[:-1], octave=int(root_note[-1]), duration=1, velocity=64),
        scale_type=scale_type
    )
    assert scale.root.note_name == root_note[:-1]
    assert scale.root.octave == int(root_note[-1])
    assert scale.scale_type == scale_type
