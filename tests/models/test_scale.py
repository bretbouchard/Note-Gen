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

@pytest.mark.asyncio
async def test_scale_type_degree_count():
    """Test the 'degree_count' property on ScaleType (should match length of get_intervals())."""
    for scale_type in ScaleType:
        scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
        scale.notes = scale._generate_scale_notes()  # Ensure notes are generated
        intervals = scale.calculate_intervals()
        degree_count_value = scale_type.degree_count
        logger.info(f"Testing {scale_type}: degree_count = {degree_count_value}, len(scale.notes) = {len(scale.notes)}")
        generated_notes = [note.note_name + str(note.octave) for note in scale.notes]
        logger.info(f"Generated notes: {generated_notes}")
        unique_notes = set(generated_notes)
        logger.info(f"Unique notes: {unique_notes}, Count: {len(unique_notes)}")
        logger.info(f"Unique note count: {len(unique_notes)}")
        logger.info(f"Unique notes details:")
        for note in unique_notes:
            logger.info(f"  - {note}")
        assert len(intervals) == len(scale.notes)
        # Ensure that the degree count matches the number of unique notes
        logger.info(f"Asserting degree_count {degree_count_value} == len(unique_notes) {len(unique_notes)}")
        assert degree_count_value == len(unique_notes)

@pytest.mark.asyncio
async def test_scale_type_is_diatonic():
    """Test which scale types are diatonic (have 7 unique notes)."""
    diatonic_scales = {
        ScaleType.MAJOR,
        ScaleType.MINOR,
        ScaleType.DORIAN,
        ScaleType.HARMONIC_MINOR,
        ScaleType.HARMONIC_MAJOR,
        ScaleType.MELODIC_MAJOR,
        ScaleType.MELODIC_MINOR,
        ScaleType.DOUBLE_HARMONIC_MAJOR,
        ScaleType.PHRYGIAN
    }
    for scale_type in ScaleType:
        scale = Scale(root=Note.from_full_name('C4'), scale_type=scale_type)
        scale.notes = scale._generate_scale_notes()  # Ensure notes are generated
        logger.info(f"Testing diatonic for {scale_type}: len(scale.notes) = {len(scale.notes)}")
        generated_notes = [note.note_name + str(note.octave) for note in scale.notes]
        logger.info(f"Generated notes: {generated_notes}")
        unique_notes = set(generated_notes)
        logger.info(f"Unique notes: {unique_notes}, Count: {len(unique_notes)}")
        logger.info(f"Unique note count: {len(unique_notes)}")
        logger.info(f"Unique notes details:")
        for note in unique_notes:
            logger.info(f"  - {note}")
        if scale_type in diatonic_scales:
            logger.info(f"Asserting len(unique_notes) == 7 for {scale_type}")
            assert len(unique_notes) == 7
        else:
            logger.info(f"Asserting len(unique_notes) != 7 for {scale_type}")
            assert len(unique_notes) != 7

        logger.info(f"Diatonic scale check for {scale_type}: {len(unique_notes)} unique notes: {unique_notes}")

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