import pytest
from src.note_gen.models.note import AccidentalType, Note
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.scale import Scale

@pytest.fixture
def some_scale_instance() -> Scale:
    return Scale(
        scale=ScaleInfo(root=Note(name='C', octave=4)),  # Provide a valid ScaleInfo instance
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )

@pytest.fixture
def setup_scale_info() -> ScaleInfo:
    return ScaleInfo(
        scale_type='major',
        root=Note(name='C', octave=4),
        scale_degrees=[
            ScaleDegree(degree=1),
            ScaleDegree(degree=2),
            ScaleDegree(degree=3),
            ScaleDegree(degree=4),
            ScaleDegree(degree=5),
            ScaleDegree(degree=6),
            ScaleDegree(degree=7)
        ],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )

def create_default_scale(scale_info: ScaleInfo) -> Scale:
    return Scale(
        scale=scale_info,
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )

def test_scale_info_initialization() -> None:
    # Test valid initialization
    scale_info = ScaleInfo(root=Note(name='C', octave=4))
    assert scale_info.root.name == 'C'
    assert scale_info.root.octave == 4

    # Test invalid initialization
    with pytest.raises(ValueError):
        ScaleInfo(root=None)

    with pytest.raises(ValueError):
        ScaleInfo(root=Note(name='C', octave=4), scale_degrees=None)

def test_scale_info_initialization_with_scale_degrees() -> None:
    # Create a valid ScaleInfo instance
    setup_scale_info = ScaleInfo(
        scale_type='major',
        root=Note(name='C', octave=4),
        scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )

    # Validate the setup_scale_info instance
    assert setup_scale_info.scale_type == 'major'
    assert setup_scale_info.root.name == 'C'
    assert setup_scale_info.root.octave == 4
    assert len(setup_scale_info.scale_degrees) == 7  # Check for 7 scale degrees
    for degree in setup_scale_info.scale_degrees:
        assert isinstance(degree, ScaleDegree)  # Check if each degree is a ScaleDegree instance

    # Create a Scale instance
    scale = Scale(
        scale=setup_scale_info,
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )
    
    # Assertions to verify the Scale instance
    assert scale.scale_info_v2 == setup_scale_info
    assert scale.numeral == 'I'
    assert scale.quality == 'major'
    assert scale.scale_degree == 1
    assert scale.is_major is True

def test_scale_validation() -> None:
    valid_scale_info = ScaleInfo(
        scale_type='major',
        root=Note(name='C', octave=4),
        scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )
    scale = Scale(
        scale=valid_scale_info,
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )
    assert scale.scale_info_v2 == valid_scale_info


def test_create_default_scale() -> None:
    default_scale_info = ScaleInfo(
        scale_type='major',
        root=Note(name='C', octave=4),
        scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )
    scale = Scale(
        scale=default_scale_info,
        numeral='I',
        numeral_str='I',
        scale_degree=1,
        quality='major',
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )
    assert scale.scale_info_v2 == default_scale_info

def test_create_default_scale_with_function() -> None:
    # Create a default ScaleInfo instance
    default_scale_info = ScaleInfo(
        scale_type='major',
        root=Note(name='C', octave=4),
        scale_degrees=[ScaleDegree(degree=i) for i in range(1, 8)],
        key_signature='C',
        intervals=[0, 2, 4, 5, 7, 9, 11],
        notes=[],
        scale_notes=[],
        scale=[]
    )
    
    scale = create_default_scale(default_scale_info)
    
    # Assertions to verify the Scale instance
    assert scale.scale_info_v2 == default_scale_info
    assert scale.numeral == 'I'
    assert scale.quality == 'major'
    assert scale.scale_degree == 1
    assert scale.is_major is True

def create_scale(scale_info: ScaleInfo, numeral: str, scale_degree: int, quality: str) -> Scale:
    return Scale(
        scale=scale_info,
        numeral=numeral,
        numeral_str=numeral,
        scale_degree=scale_degree,
        quality=quality,
        is_major=True,
        is_diminished=False,
        is_augmented=False,
        is_half_diminished=False,
        has_seventh=False,
        has_ninth=False,
        has_eleventh=False,
        inversion=0
    )

scale = some_scale_instance