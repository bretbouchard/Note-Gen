import pytest
from src.note_gen.models.note import Note
from src.note_gen.models.scale import Scale, ScaleType

@pytest.mark.parametrize(
    "root_name, scale_type",
    [
        ("C4", ScaleType.MAJOR),
        ("D3", ScaleType.NATURAL_MINOR),
        ("A4", ScaleType.HARMONIC_MINOR),
        ("G2", ScaleType.DORIAN),
        ("C4", ScaleType.CHROMATIC),
        ("E4", ScaleType.MINOR_PENTATONIC),
        ("B3", ScaleType.MAJOR_PENTATONIC),
        ("F4", ScaleType.NEAPOLITAN_MAJOR),
        ("A3", ScaleType.NEAPOLITAN_MINOR),
        ("C5", ScaleType.HARMONIC_MAJOR),
        ("D4", ScaleType.MELODIC_MAJOR),
        ("E5", ScaleType.DOUBLE_HARMONIC_MAJOR),
        ("F5", ScaleType.BYZANTINE),
        ("G5", ScaleType.HUNGARIAN_MINOR),
        ("A5", ScaleType.HUNGARIAN_MAJOR),
        ("B5", ScaleType.ROMANIAN_MINOR),
        ("C6", ScaleType.ULTRAPHRYGIAN),
        ("D6", ScaleType.YONANAI),
        ("E6", ScaleType.JAPANESE),
        ("F6", ScaleType.INDIAN),
        ("G6", ScaleType.CHINESE),
        ("A6", ScaleType.BALINESE),
        ("B6", ScaleType.PERSIAN),
    ]
)
def test_scale_creation_and_notes(root_name: str, scale_type: ScaleType) -> None:
    """
    Test creating various Scales and generating their notes.
    """
    root_note = Note.from_name(root_name)
    scale = Scale(root_note, scale_type)
    notes = scale.get_notes()

    # Basic checks:
    assert notes[0] == root_note, "First note of scale should be the root."
    assert len(notes) == len(scale_type.get_intervals()) + 1, (
        "Number of notes should be number of intervals + 1."
    )

    # Check each subsequent note is transposed by the scale intervals
    current_midi = root_note.midi_number
    for interval, note in zip(scale_type.get_intervals(), notes[1:]):
        current_midi += interval
        assert note.midi_number == current_midi, (
            f"Scale note does not match interval step {interval}."
        )


@pytest.mark.parametrize(
    "root_name, scale_type, valid_degree",
    [
        ("C4", ScaleType.MAJOR, 1),
        ("C4", ScaleType.MAJOR, 7),
        ("C4", ScaleType.HARMONIC_MINOR, 7),  
    ]
)
def test_get_scale_degree_valid(root_name: str, scale_type: ScaleType, valid_degree: int) -> None:
    """
    Test getting a valid scale degree (within range).
    """
    root_note = Note.from_name(root_name)
    scale = Scale(root_note, scale_type)

    note_at_degree = scale.get_scale_degree(valid_degree)
    assert note_at_degree is not None, "Should return a valid Note object."


@pytest.mark.parametrize(
    "root_name, scale_type, invalid_degree",
    [
        ("C4", ScaleType.MAJOR, 0),   # below range
        ("C4", ScaleType.MAJOR, 8),   # major has 7 intervals => 8 is out-of-range
        ("C4", ScaleType.CHROMATIC, 13),  # chromatic has 12 intervals => 13 out-of-range
    ]
)
def test_get_scale_degree_invalid(root_name: str, scale_type: ScaleType, invalid_degree: int) -> None:
    """
    Test that get_scale_degree raises an error for an out-of-range degree.
    """
    root_note = Note.from_name(root_name)
    scale = Scale(root_note, scale_type)

    with pytest.raises(ValueError, match="Scale degree must be between 1 and"):
        scale.get_scale_degree(invalid_degree)


def test_scale_type_degree_count() -> None:
    """
    Test the 'degree_count' property on ScaleType (should match length of get_intervals()).
    """
    for stype in ScaleType:
        expected_count = len(stype.get_intervals())
        assert stype.degree_count == expected_count, (
            f"degree_count mismatch for {stype}. "
            f"Expected {expected_count}, got {stype.degree_count}"
        )


def test_scale_type_is_diatonic() -> None:
    """
    Test the 'is_diatonic' property on ScaleType.
    Diatonic scales (like MAJOR, NATURAL_MINOR, etc.) have 7 intervals.
    Others (like pentatonic, blues, chromatic) do not.
    """
    diatonic_scales = [
        ScaleType.MAJOR, ScaleType.NATURAL_MINOR, ScaleType.HARMONIC_MINOR,
        ScaleType.MELODIC_MINOR, ScaleType.DORIAN, ScaleType.PHRYGIAN,
        ScaleType.LYDIAN, ScaleType.MIXOLYDIAN, ScaleType.LOCRIAN
    ]
    for ds in diatonic_scales:
        assert ds.is_diatonic, f"{ds} should be diatonic but is_diatonic is False."
    
    non_diatonic_scales = [
        ScaleType.PENTATONIC_MAJOR, ScaleType.PENTATONIC_MINOR,
        ScaleType.BLUES, ScaleType.CHROMATIC, ScaleType.WHOLE_TONE
    ]
    for nds in non_diatonic_scales:
        assert not nds.is_diatonic, f"{nds} should not be diatonic but is_diatonic is True."


def test_scale_type_get_scale_degrees() -> None:
    """
    Test 'get_scale_degrees' returns [1 .. (len(get_intervals()) + 1)].
    """
    for stype in ScaleType:
        intervals_len = len(stype.get_intervals())
        expected_degrees = list(range(1, intervals_len + 1))
        assert stype.get_scale_degrees() == expected_degrees, (
            f"{stype} scale degrees do not match {expected_degrees}."
        )


@pytest.mark.parametrize(
    "scale_type, in_range_degree, out_of_range_degree",
    [
        (ScaleType.MAJOR, 3, 8),           # major=7 intervals => valid up to 7
        (ScaleType.PENTATONIC_MAJOR, 4, 6), # pentatonic_major=5 intervals => valid up to 6
        (ScaleType.CHROMATIC, 10, 13),     # chromatic=12 intervals => valid up to 13
    ]
)
def test_scale_type_validate_degree(
    scale_type: ScaleType,
    in_range_degree: int,
    out_of_range_degree: int
) -> None:
    """
    Test 'validate_degree' for valid and invalid degrees.
    """
    # Valid
    assert scale_type.validate_degree(in_range_degree) is True

    # Invalid
    with pytest.raises(ValueError, match="Invalid scale degree:"):
        scale_type.validate_degree(out_of_range_degree)