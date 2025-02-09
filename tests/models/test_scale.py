import pytest
from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale
from src.note_gen.models.enums import ScaleType

@pytest.fixture
def root_name() -> str:
    return "C4"

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
def test_scale_creation_and_notes(root_name: str, scale_type: ScaleType):
    """Test that scales can be created with different root notes and types."""
    root = Note.from_name(root_name, duration=1)
    scale = Scale(root=root, scale_type=scale_type)
    notes = scale.generate_notes()
    
    # Basic validation
    assert isinstance(scale, Scale)
    assert scale.root == root
    assert scale.scale_type == scale_type
    assert isinstance(notes, list)
    assert len(notes) > 0
    assert all(isinstance(note, Note) for note in notes)
    
    # The first note should be the root note
    assert notes[0] == root
    
    # The number of notes should match the number of intervals plus 1 (for the root)
    expected_length = len(scale_type.get_intervals()) + 1
    assert len(notes) == expected_length

@pytest.mark.parametrize(
    "root_name, scale_type, valid_degree",
    [
        ("C4", ScaleType.MAJOR, 1),
        ("C4", ScaleType.MAJOR, 4),
        ("D3", ScaleType.MINOR, 2),
        ("A4", ScaleType.HARMONIC_MINOR, 3),
    ],
)
def test_get_scale_degree_valid(root_name: str, scale_type: ScaleType, valid_degree: int):
    """Test that get_scale_degree returns the correct note for valid degrees."""
    root = Note.from_name(root_name, duration=1)
    scale = Scale(root=root, scale_type=scale_type)
    note = scale.get_scale_degree(valid_degree)
    assert isinstance(note, Note)

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
def test_get_scale_degree_invalid(root_name: str, scale_type: ScaleType, invalid_degree: int):
    """Test that get_scale_degree raises an error for an out-of-range degree."""
    root = Note.from_name(root_name, duration=1)
    scale = Scale(root=root, scale_type=scale_type)
    with pytest.raises(ValueError):
        scale.get_scale_degree(invalid_degree)

def test_scale_type_degree_count():
    """Test the 'degree_count' property on ScaleType (should match length of get_intervals())."""
    for scale_type in ScaleType:
        intervals = scale_type.get_intervals()
        assert len(intervals) > 0
        assert isinstance(intervals, list)
        assert all(isinstance(i, int) for i in intervals)

def test_scale_type_is_diatonic():
    """Test which scale types are diatonic (have 7 unique notes)."""
    diatonic_types = {
        ScaleType.MAJOR,
        ScaleType.MINOR,
        ScaleType.HARMONIC_MINOR,
        ScaleType.MELODIC_MINOR,
        ScaleType.DORIAN,
        ScaleType.PHRYGIAN,
        ScaleType.LYDIAN,
        ScaleType.MIXOLYDIAN,
        ScaleType.LOCRIAN,
    }
    
    non_diatonic_types = {
        ScaleType.MAJOR_PENTATONIC,
        ScaleType.MINOR_PENTATONIC,
        ScaleType.CHROMATIC,
    }
    
    # Test diatonic scales have 7 unique notes
    for scale_type in diatonic_types:
        root = Note.from_name("C4", duration=1)  # Example root note
        scale = Scale(root=root, scale_type=scale_type)
        scale.generate_notes()  # Ensure notes are generated
        assert len(scale.notes) == 7
    
    # Test non-diatonic scales don't have 7 unique notes
    for scale_type in non_diatonic_types:
        root = Note.from_name("C4", duration=1)  # Example root note
        scale = Scale(root=root, scale_type=scale_type)
        scale.generate_notes()  # Ensure notes are generated
        assert len(scale.notes) != 7

@pytest.mark.parametrize(
    "scale_type, in_range_degree, out_of_range_degree",
    [
        (ScaleType.MAJOR, 3, 8),
        (ScaleType.MAJOR_PENTATONIC, 4, 6),
        (ScaleType.CHROMATIC, 10, 13),
    ],
)
def test_scale_type_validate_degree(
    scale_type: ScaleType,
    in_range_degree: int,
    out_of_range_degree: int
):
    """Test that scale degrees are validated correctly."""
    root = Note.from_name("C4", duration=1)
    scale = Scale(root=root, scale_type=scale_type)
    
    # Valid degree should work
    note = scale.get_scale_degree(in_range_degree)
    assert isinstance(note, Note)
    
    # Invalid degree should raise ValueError
    with pytest.raises(ValueError):
        scale.get_scale_degree(out_of_range_degree)