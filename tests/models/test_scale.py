import pytest
from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.enums import ScaleType
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def root_name() -> str:
    return "C4"

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "root_name, scale_type",
    [
        ("C4", ScaleType.MAJOR),
        ("D3", ScaleType.MINOR),
        ("A4", ScaleType.HARMONIC_MINOR),
        ("G2", ScaleType.DORIAN),
        ("C4", ScaleType.CHROMATIC),
        ("E4", ScaleType.MINOR_PENTATONIC),
        ("B3", ScaleType.MAJOR_PENTATONIC),
        ("C5", ScaleType.HARMONIC_MAJOR),
        ("D4", ScaleType.MELODIC_MAJOR),
        ("E5", ScaleType.DOUBLE_HARMONIC_MAJOR),
    ],
)
async def test_scale_creation_and_notes(root_name: str, scale_type: ScaleType):
    """Test that scale creation and note retrieval work correctly."""
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
    scale.notes = scale._generate_scale_notes()  # Ensure notes are generated
    assert scale.root.note_name == root_name.rstrip('0123456789')
    assert scale.scale_type == scale_type
    assert len(scale.notes) > 0

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "root_name, scale_type, degree",
    [
        ("C4", ScaleType.MAJOR, 1),
        ("C4", ScaleType.MAJOR, 4),
        ("D3", ScaleType.MINOR, 2),
        ("A4", ScaleType.HARMONIC_MINOR, 3),
    ],
)
async def test_get_scale_degree_valid(root_name: str, scale_type: ScaleType, degree: int):
    """Test that get_scale_degree returns the correct note for valid degrees."""
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
    scale.notes = scale._generate_scale_notes()  # Ensure notes are generated
    note = scale.get_scale_degree(degree)
    assert note is not None
    assert isinstance(note, Note)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "root_name, scale_type, invalid_degree",
    [
        ("C4", ScaleType.MAJOR, 0),
        ("C4", ScaleType.MAJOR, 8),
        ("C4", ScaleType.CHROMATIC, 13),
        ("D3", ScaleType.MINOR, -1),
        ("A4", ScaleType.HARMONIC_MINOR, 8),
        ("G2", ScaleType.DORIAN, 0),
    ],
)
async def test_get_scale_degree_invalid(root_name: str, scale_type: ScaleType, invalid_degree: int):
    """Test that get_scale_degree raises an error for an out-of-range degree."""
    scale = Scale(root=Note.from_full_name(root_name), scale_type=scale_type)
    scale.notes = scale._generate_scale_notes()  # Ensure notes are generated
    with pytest.raises(ValueError):
        scale.get_scale_degree(invalid_degree)

def test_scale_type_degree_count():
    """Test that each scale type has the correct number of degrees."""
    scale_types = [
        ScaleType.MAJOR,
        ScaleType.MINOR,
        ScaleType.HARMONIC_MINOR,
        ScaleType.MELODIC_MINOR,
        ScaleType.DORIAN,
        ScaleType.PHRYGIAN,
        ScaleType.LYDIAN,
        ScaleType.MIXOLYDIAN,
        ScaleType.LOCRIAN,
        ScaleType.PENTATONIC_MAJOR,
        ScaleType.PENTATONIC_MINOR,
        ScaleType.BLUES,
        ScaleType.CHROMATIC,
    ]
    
    expected_degrees = {
        ScaleType.MAJOR: 7,
        ScaleType.MINOR: 7,
        ScaleType.HARMONIC_MINOR: 7,
        ScaleType.MELODIC_MINOR: 7,
        ScaleType.DORIAN: 7,
        ScaleType.PHRYGIAN: 7,
        ScaleType.LYDIAN: 7,
        ScaleType.MIXOLYDIAN: 7,
        ScaleType.LOCRIAN: 7,
        ScaleType.PENTATONIC_MAJOR: 5,
        ScaleType.PENTATONIC_MINOR: 5,
        ScaleType.BLUES: 6,
        ScaleType.CHROMATIC: 12,
    }
    
    for scale_type in scale_types:
        scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
        assert scale.degree_count == expected_degrees[scale_type], \
            f"Expected {expected_degrees[scale_type]} degrees for {scale_type}, got {scale.degree_count}"

@pytest.mark.asyncio
async def test_scale_type_is_diatonic():
    """Test which scale types are diatonic (have 7 unique notes)."""
    supported_scales = {
        ScaleType.MAJOR,
        ScaleType.MINOR,
        ScaleType.DORIAN,
        ScaleType.PHRYGIAN,
        ScaleType.LYDIAN,
        ScaleType.MIXOLYDIAN,
        ScaleType.LOCRIAN,
        ScaleType.HARMONIC_MINOR,
        ScaleType.HARMONIC_MAJOR,
        ScaleType.MELODIC_MINOR,
        ScaleType.MELODIC_MAJOR,
        ScaleType.DOUBLE_HARMONIC_MAJOR
    }
    
    diatonic_scales = supported_scales  # All our supported scales are diatonic
    
    for scale_type in supported_scales:  # Only test supported scales
        scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
        scale.notes = scale._generate_scale_notes()
        unique_notes = set(note.note_name + str(note.octave) for note in scale.notes)
        
        if scale_type in diatonic_scales:
            assert len(unique_notes) == 7, f"{scale_type} should have 7 unique notes"
        else:
            assert len(unique_notes) != 7, f"{scale_type} should not have 7 unique notes"

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scale_type, in_range_degree, out_of_range_degree",
    [
        (ScaleType.MAJOR, 3, 8),
        (ScaleType.MAJOR_PENTATONIC, 4, 6),
        (ScaleType.CHROMATIC, 10, 13),
    ],
)
async def test_scale_type_validate_degree(scale_type: ScaleType, in_range_degree: int, out_of_range_degree: int):
    """Test that scale degrees are validated correctly."""
    scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
    scale.notes = scale._generate_scale_notes()  # Ensure notes are generated
    # Valid degree should not raise error
    scale.get_scale_degree(in_range_degree)
    # Invalid degree should raise error
    with pytest.raises(ValueError):
        scale.get_scale_degree(out_of_range_degree)