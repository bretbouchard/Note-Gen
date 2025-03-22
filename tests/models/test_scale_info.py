import pytest
from pydantic import ValidationError
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.note import Note
from src.note_gen.core.enums import ScaleType, ChordQuality
from typing import List, Optional

@pytest.fixture
def c_major_scale() -> ScaleInfo:
    return ScaleInfo(
        root=Note(
            note_name="C",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type=ScaleType.MAJOR,
        key="C4"
    )

@pytest.fixture
def a_minor_scale() -> ScaleInfo:
    return ScaleInfo(
        root=Note(
            note_name="A",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type=ScaleType.MINOR,
        key="A4"
    )

# Test validation of root note
def test_valid_root_note() -> None:
    # Test with valid Note object
    scale: ScaleInfo = ScaleInfo(
        root=Note(
            note_name="C",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type=ScaleType.MAJOR
    )
    assert isinstance(scale.root, Note)
    assert scale.root.note_name == "C"
    assert scale.root.octave == 4

    # Test with valid string
    scale: ScaleInfo = ScaleInfo(
        root=Note.from_full_name("C4"),
        scale_type=ScaleType.MAJOR
    )
    assert isinstance(scale.root, Note)
    assert scale.root.note_name == "C"
    assert scale.root.octave == 4

def test_invalid_root_note() -> None:
    with pytest.raises(ValidationError):
        ScaleInfo(
            root="invalid_note",
            scale_type=ScaleType.MAJOR
        )

    with pytest.raises(ValidationError):
        ScaleInfo(
            root=123,
            scale_type=ScaleType.MAJOR
        )

    with pytest.raises(ValidationError):
        ScaleInfo(
            root=Note(
                note_name="invalid",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

    with pytest.raises(ValidationError):
        ScaleInfo(
            root=None,
            scale_type=ScaleType.MAJOR
        )

    with pytest.raises(ValidationError):
        ScaleInfo(
            root="",
            scale_type=ScaleType.MAJOR
        )

    with pytest.raises(ValidationError):
        ScaleInfo(
            root="C",
            scale_type="invalid_type"
        )

    with pytest.raises(ValidationError):
        ScaleInfo(
            root=Note(
                note_name="C",
                octave=8,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

# Test validation of scale type
def test_valid_scale_type() -> None:
    # Test with valid ScaleType enum
    scale: ScaleInfo = ScaleInfo(
        root=Note(
            note_name="C",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type=ScaleType.MAJOR
    )
    assert scale.scale_type == ScaleType.MAJOR

    # Test with valid string
    scale: ScaleInfo = ScaleInfo(
        root=Note(
            note_name="C",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type="MAJOR"
    )
    assert scale.scale_type == ScaleType.MAJOR

def test_invalid_scale_type() -> None:
    with pytest.raises(ValidationError):
        ScaleInfo(
            root=Note(
                note_name="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type="invalid_type"
        )

    with pytest.raises(ValidationError):
        ScaleInfo(
            root=Note(
                note_name="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
            ),
            scale_type=123
        )

# Test key/root synchronization
def test_key_root_synchronization() -> None:
    # Test setting key without root
    scale = ScaleInfo(
        key="C4",
        root=Note(
            note_name="C",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type=ScaleType.MAJOR
    )
    assert scale.root.note_name == "C"
    assert scale.root.octave == 4

    # Test setting root without key
    scale = ScaleInfo(
        root="C",
        scale_type=ScaleType.MAJOR
    )
    assert scale.key == "C4"

    # Test setting both key and root
    scale = ScaleInfo(
        key="C4",
        root="C",
        scale_type=ScaleType.MAJOR
    )
    assert scale.key == "C4"
    assert scale.root.note_name == "C"
    assert scale.root.octave == 4

    # Test invalid key format
    with pytest.raises(ValidationError):
        ScaleInfo(
            key="invalid_format",
            root=Note(
                note_name="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

    # Test invalid key note
    with pytest.raises(ValidationError):
        ScaleInfo(
            key="X4",
            root=Note(
                note_name="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

    # Test invalid key octave
    with pytest.raises(ValidationError):
        ScaleInfo(
            key="C-1",
            root=Note(
                note_name="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

    # Test invalid key octave (too high)
    with pytest.raises(ValidationError):
        ScaleInfo(
            key="C10",
            root=Note(
                note_name="C",
                octave=4,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

    # Test invalid root note
    with pytest.raises(ValidationError):
        ScaleInfo(
            root="invalid_note",
            scale_type=ScaleType.MAJOR
        )

    # Test invalid root octave
    with pytest.raises(ValidationError):
        ScaleInfo(
            root=Note(
                note_name="C",
                octave=10,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

    # Test invalid root octave (too low)
    with pytest.raises(ValidationError):
        ScaleInfo(
            root=Note(
                note_name="C",
                octave=-1,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            ),
            scale_type=ScaleType.MAJOR
        )

    # Test root as string
    scale = ScaleInfo(
        root="C4",
        scale_type=ScaleType.MAJOR
    )
    assert scale.root.note_name == "C"
    assert scale.root.octave == 4

    # Test root as integer
    with pytest.raises(ValidationError):
        ScaleInfo(
            root=123,
            scale_type=ScaleType.MAJOR
        )

# Test scale note generation
def test_get_scale_notes(c_major_scale: ScaleInfo, a_minor_scale: ScaleInfo) -> None:
    # Test C major scale
    c_major_notes: List[Note] = c_major_scale.get_scale_notes()
    expected_notes = ["C", "D", "E", "F", "G", "A", "B"]
    assert [note.note_name for note in c_major_notes] == expected_notes

    # Test A minor scale
    a_minor_notes: List[Note] = a_minor_scale.get_scale_notes()
    expected_notes = ["A", "B", "C", "D", "E", "F", "G"]
    assert [note.note_name for note in a_minor_notes] == expected_notes

# Test note degree calculation
def test_note_degree_calculation(c_major_scale: ScaleInfo) -> None:
    # Test positive degrees (C major scale: C D E F G A B)
    expected_notes = ["C", "D", "E", "F", "G", "A", "B", "C"]
    for degree in range(1, 9):
        note = c_major_scale.get_note_for_degree(degree)
        assert note.note_name == expected_notes[degree - 1]
        assert note.octave == 4 + ((degree - 1) // 7)

    # Test negative degrees
    expected_notes = ["B", "A", "G", "F", "E", "D", "C", "B"]
    for degree in range(-1, -9, -1):
        note = c_major_scale.get_note_for_degree(degree)
        assert note.note_name == expected_notes[-degree - 1]
        assert note.octave == 3 + ((-degree - 1) // 7)

# Test scale quality mappings
def test_scale_qualities() -> None:
    major_scale: ScaleInfo = ScaleInfo(
        root=Note(
            note_name="C",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type=ScaleType.MAJOR
    )
    minor_scale: ScaleInfo = ScaleInfo(
        root=Note(
            note_name="A",
            octave=4,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        ),
        scale_type=ScaleType.MINOR
    )

    # Test major scale qualities
    assert len(major_scale.MAJOR_SCALE_QUALITIES) == 7
    assert major_scale.MAJOR_SCALE_QUALITIES[0] == ChordQuality.MAJOR
    assert major_scale.MAJOR_SCALE_QUALITIES[6] == ChordQuality.DIMINISHED

    # Test minor scale qualities
    assert len(minor_scale.MINOR_SCALE_QUALITIES) == 7
    assert minor_scale.MINOR_SCALE_QUALITIES[0] == ChordQuality.MINOR
    assert minor_scale.MINOR_SCALE_QUALITIES[6] == ChordQuality.MAJOR

# Test scale creation
def test_get_scale(c_major_scale: ScaleInfo) -> None:
    scale: Optional[ScaleInfo] = c_major_scale.get_scale()
    assert scale is not None
    assert scale.root.note_name == "C"
    assert scale.scale_type == ScaleType.MAJOR

# Test edge cases
def test_edge_cases(c_major_scale: ScaleInfo) -> None:
    # Test very high degree
    note = c_major_scale.get_note_for_degree(20)
    assert note.note_name == "C"
    assert note.octave == 6

    # Test very low degree
    note = c_major_scale.get_note_for_degree(-20)
    assert note.note_name == "C"
    assert note.octave == 2

    # Test zero degree (should raise error)
    with pytest.raises(ValueError):
        c_major_scale.get_note_for_degree(0)

    # Test non-integer degree
    with pytest.raises(TypeError):
        c_major_scale.get_note_for_degree(1.5)

    # Test special case for degree -1
    note = c_major_scale.get_note_for_degree(-1)
    assert note.note_name == "B"
    assert note.octave == 3

    # Test degree -2
    note = c_major_scale.get_note_for_degree(-2)
    assert note.note_name == "A"
    assert note.octave == 3

    # Test degree -3
    note = c_major_scale.get_note_for_degree(-3)
    assert note.note_name == "G"
    assert note.octave == 3

    # Test degree 1 (should be root note)
    note = c_major_scale.get_note_for_degree(1)
    assert note.note_name == "C"
    assert note.octave == 4

    # Test degree 8 (should be C in next octave)
    note = c_major_scale.get_note_for_degree(8)
    assert note.note_name == "C"
    assert note.octave == 5
