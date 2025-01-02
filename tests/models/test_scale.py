"""
Module for testing musical scales.
"""

import pytest
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale_degree import ScaleDegree

@pytest.fixture
def some_scale_instance() -> Scale:
    root_note = Note.from_name("C4")
    return Scale(
        root=root_note,
        quality="major",
        scale_type='major',
        scale_info_v2=ScaleInfo(
            scale_type='major',
            root=root_note,
            scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
            key_signature='C',
            intervals=[0, 2, 4, 5, 7, 9, 11],
            notes=[],
            scale_notes=[],
            scale=[]
        )
    )

def test_scale_info_initialization() -> None:
    # Test valid initialization
    scale_info = ScaleInfo(root=Note.from_name('C4'))
    assert scale_info.root.note_name == 'C'
    assert scale_info.root.octave == 4

    # Test invalid initialization
    with pytest.raises(ValueError):
        ScaleInfo(root=None)

    with pytest.raises(ValueError):
        ScaleInfo(root=Note.from_name('C4'), scale_type='invalid')

def test_scale_info_initialization_with_scale_degrees() -> None:
    # Create a valid ScaleInfo instance
    setup_scale_info = ScaleInfo(
        scale_type='major',
        root=Note.from_name('C4'),
        scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )

    # Validate the setup_scale_info instance
    assert setup_scale_info.scale_type == 'major'
    assert setup_scale_info.root.note_name == 'C'
    assert setup_scale_info.root.octave == 4
    assert len(setup_scale_info.scale_degrees) == 7  # Check for 7 scale degrees
    for degree in setup_scale_info.scale_degrees:
        assert isinstance(degree, ScaleDegree)  # Check if each degree is a ScaleDegree instance

    # Create a Scale instance
    scale = Scale(
        root=setup_scale_info.root,
        scale_info_v2=setup_scale_info,
        quality='major',
        scale_type='major'
    )
    assert scale.root == setup_scale_info.root
    assert scale.quality == 'major'

def test_scale_validation() -> None:
    valid_scale_info = ScaleInfo(
        scale_type='major',
        root=Note.from_name('C4'),
        scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )
    scale = Scale(
        root=valid_scale_info.root,
        scale_info_v2=valid_scale_info,
        quality='major',
        scale_type='major'
    )
    assert scale.root == valid_scale_info.root
    assert scale.quality == 'major'

    # Test invalid quality
    with pytest.raises(ValueError):
        Scale(
            root=valid_scale_info.root,
            scale_info_v2=valid_scale_info,
            quality='invalid',
            scale_type='major'
        )

def test_create_default_scale() -> None:
    root = Note.from_name('C4')
    scale = Scale.create_default(root=root, quality='major')
    assert scale.root == root
    assert scale.quality == 'major'
    assert scale.is_major is True
    assert scale.numeral == 'I'

def test_create_default_scale_with_function() -> None:
    # Create a default ScaleInfo instance
    default_scale_info = ScaleInfo(
        scale_type='major',
        root=Note.from_name('C4'),
        scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )

    scale = Scale(
        root=default_scale_info.root,
        scale_info_v2=default_scale_info,
        quality='major',
        scale_type='major'
    )
    assert scale.root == default_scale_info.root
    assert scale.quality == 'major'

def create_default_scale(scale_info: ScaleInfo) -> Scale:
    return Scale(
        root=scale_info.root,
        scale_info_v2=scale_info,
        quality='major',
        scale_type='major'
    )