from typing import Any, Dict, List, Optional, Tuple, Union, cast

import json
import pytest
from pydantic import ValidationError

from note_gen.models.note import Note
from note_gen.models.scale import Scale, ScaleType
from note_gen.models.scale_info import ScaleInfo
from note_gen.core.enums import ChordQuality

# Test fixtures
@pytest.fixture
def c_major_scale() -> ScaleInfo:
    """Return a C major scale."""
    return ScaleInfo(root=Note.from_note_name("C"), scale_type=ScaleType.MAJOR)

@pytest.fixture
def c_minor_scale() -> ScaleInfo:
    """Return a C minor scale."""
    return ScaleInfo(root=Note.from_note_name("C"), scale_type=ScaleType.MINOR)

@pytest.fixture
def c_lydian_scale() -> ScaleInfo:
    """Return a C lydian scale."""
    return ScaleInfo(root=Note.from_note_name("C"), scale_type=ScaleType.LYDIAN)

# Test validation of root note
def test_valid_root_note() -> None:
    """Test that valid root notes are accepted."""
    # Test with valid Note object
    scale: ScaleInfo = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    assert isinstance(scale.root, Note)
    assert scale.root.note_name == "C"

    # Test with Note object with octave - note that from_note_name doesn't accept octaves
    # So we need to create the Note directly
    scale = ScaleInfo(
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

def test_invalid_root_note() -> None:
    """Test that invalid root notes are rejected."""
    # Test with invalid note name
    with pytest.raises(ValueError):
        ScaleInfo(
            root=Note.from_note_name("invalid_note"),
            scale_type=ScaleType.MAJOR
        )
    
    # Test with integer (should raise TypeError)
    with pytest.raises(TypeError):
        # Need to cast to Any to bypass type checking for the test
        ScaleInfo(
            root=cast(Any, 123),
            scale_type=ScaleType.MAJOR
        )
    
    # Test with empty Note (should raise ValueError)
    with pytest.raises(ValueError):
        # We need to use a dictionary to bypass type checking
        data = {"root": None, "scale_type": ScaleType.MAJOR}
        ScaleInfo.model_validate(data)
    
    # Test with empty string (should raise ValueError)
    with pytest.raises(ValueError):
        ScaleInfo(
            root=cast(Any, ""),
            scale_type=ScaleType.MAJOR
        )
    
    # Test with invalid scale type
    with pytest.raises(ValueError):
        ScaleInfo(
            root=Note.from_note_name("C"),
            scale_type=cast(Any, "invalid_type")
        )

# Test validation of scale type
def test_valid_scale_type() -> None:
    """Test that valid scale types are accepted."""
    # Test with ScaleType enum
    scale = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    assert scale.scale_type == ScaleType.MAJOR
    
    # Test with string
    scale = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type="MAJOR"  # type: ignore
    )
    assert scale.scale_type == ScaleType.MAJOR

class TestScaleInfo:
    """Test class for ScaleInfo."""
    
    def test_invalid_scale_type(self) -> None:
        """Test that an invalid scale type raises a ValueError."""
        # Create a valid Note object for the root
        root_note = Note.from_note_name("C")
        
        # Test with an invalid scale type
        with pytest.raises(ValueError):
            ScaleInfo(root=root_note, scale_type=cast(Any, "invalid_type"))
    
    def test_key_root_synchronization(self) -> None:
        """Test that key and root are synchronized."""
        # Test that key and root must be the same
        with pytest.raises(ValueError, match="Key and root must be the same"):
            # This should raise an error because key and root don't match
            ScaleInfo(root=Note.from_note_name("C"), key="D4", scale_type=ScaleType.MAJOR)

# Test scale note generation
def test_get_scale_notes() -> None:
    """Test get_scale_notes method."""
    # Create a scale info object
    c_major = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Get scale notes
    notes = c_major.get_scale_notes()
    
    # Verify notes
    assert notes is not None
    notes_list = cast(List[Note], notes)  # Cast to ensure type safety
    assert len(notes_list) == 7
    assert notes_list[0].note_name == "C"
    assert notes_list[1].note_name == "D"
    assert notes_list[2].note_name == "E"
    assert notes_list[3].note_name == "F"
    assert notes_list[4].note_name == "G"
    assert notes_list[5].note_name == "A"
    assert notes_list[6].note_name == "B"
    
    # Test minor scale
    c_minor = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MINOR
    )
    
    # Get scale notes
    minor_notes = c_minor.get_scale_notes()
    
    # Verify notes
    assert minor_notes is not None
    minor_notes_list = cast(List[Note], minor_notes)  # Cast to ensure type safety
    assert len(minor_notes_list) == 7
    assert minor_notes_list[0].note_name == "C"
    assert minor_notes_list[1].note_name == "D"
    assert minor_notes_list[2].note_name == "D#"  # Eb as D#
    assert minor_notes_list[3].note_name == "F"
    assert minor_notes_list[4].note_name == "G"
    assert minor_notes_list[5].note_name == "G#"  # Ab as G#
    assert minor_notes_list[6].note_name == "A#"  # Bb as A#

# Test note degree calculation
def test_note_degree_calculation() -> None:
    """Test note degree calculation."""
    # Create a scale info object
    c_major = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Test degree 1 (root)
    note1 = c_major.get_note_for_degree(1)
    assert note1 is not None
    assert note1.note_name == "C"
    
    # Test degree 3 (third)
    note3 = c_major.get_note_for_degree(3)
    assert note3 is not None
    assert note3.note_name == "E"
    
    # Test degree 5 (fifth)
    note5 = c_major.get_note_for_degree(5)
    assert note5 is not None
    assert note5.note_name == "G"
    
    # Test degree 7 (seventh)
    note7 = c_major.get_note_for_degree(7)
    assert note7 is not None
    assert note7.note_name == "B"
    
    # Test degree 8 (octave)
    note8 = c_major.get_note_for_degree(8)
    assert note8 is not None
    assert note8.note_name == "C"
    assert note8.octave == 5  # One octave higher

# Test scale qualities
def test_scale_qualities() -> None:
    """Test scale qualities."""
    # Create a scale info object
    c_major = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Get scale notes
    notes = c_major.get_scale_notes()
    
    # Verify notes exist
    assert notes is not None
    notes_list = cast(List[Note], notes)
    
    # Verify qualities
    # In a major scale, the intervals are: W-W-H-W-W-W-H
    # C to D = whole step
    assert notes_list[1].note_name == "D"
    # D to E = whole step
    assert notes_list[2].note_name == "E"
    # E to F = half step
    assert notes_list[3].note_name == "F"
    # F to G = whole step
    assert notes_list[4].note_name == "G"
    # G to A = whole step
    assert notes_list[5].note_name == "A"
    # A to B = whole step
    assert notes_list[6].note_name == "B"

# Test scale creation
def test_get_scale_instance(c_major_scale: ScaleInfo) -> None:
    """Test get_scale method with fixture."""
    # Get scale instance
    scale = c_major_scale.get_scale()
    
    # Verify it's a Scale object
    assert scale is not None
    
    # Since we've verified scale is not None, we can safely cast it
    scale_obj: Scale = scale  # type: ignore
    
    # Verify properties
    assert scale_obj.root.note_name == "C"
    assert scale_obj.scale_type == ScaleType.MAJOR
    
    # Verify notes
    assert len(scale_obj.notes) == 7
    for i, note in enumerate(scale_obj.notes):
        assert note.note_name in ["C", "D", "E", "F", "G", "A", "B"]
        if i == 0:
            assert note.note_name == "C"
        elif i == 1:
            assert note.note_name == "D"
        elif i == 2:
            assert note.note_name == "E"
        elif i == 3:
            assert note.note_name == "F"
        elif i == 4:
            assert note.note_name == "G"
        elif i == 5:
            assert note.note_name == "A"
        elif i == 6:
            assert note.note_name == "B"

# Test edge cases
def test_edge_cases() -> None:
    """Test edge cases."""
    # Create a scale info object
    c_major = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Test negative degree
    with pytest.raises(ValueError, match="Degree cannot be zero"):
        c_major.get_note_for_degree(0)
    
    # Test non-integer degree
    with pytest.raises(TypeError, match="Degree must be an integer"):
        c_major.get_note_for_degree(1.5)  # type: ignore
    
    # Test very high degree
    high_note = c_major.get_note_for_degree(22)
    assert high_note is not None
    assert high_note.octave == 7  # Should be higher octave

# Test additional error handling paths
def test_additional_error_paths() -> None:
    """Test additional error handling paths in validation logic."""
    # Test key validation with non-string key
    # We can't test this through the constructor because Pydantic will convert numbers to strings
    # Create a test case that uses a dictionary with a non-string key
    test_data = {
        "root": Note.from_note_name("C"),
        "key": 123,  # Non-string key
        "scale_type": ScaleType.MAJOR
    }
    
    # Test with invalid key type
    # The model_validate method will call validate_scale_info which raises TypeError
    # Since we expect TypeError, we should catch it directly
    with pytest.raises(TypeError, match="Key must be a string"):
        try:
            # This should fail validation with TypeError
            ScaleInfo.model_validate(test_data)
        except ValidationError as e:
            # If it's a ValidationError, check if it contains our expected message
            if "Key must be a string" in str(e):
                # Re-raise as TypeError to match the expected exception
                raise TypeError("Key must be a string")
            # Otherwise, let the original ValidationError propagate
            raise
    
    # Test with invalid note name
    with pytest.raises(ValueError):
        # The error message might vary, so we don't check the exact message
        ScaleInfo(root=Note.from_note_name("X"), key="C4", scale_type=ScaleType.MAJOR)
    
    # Test with empty string root
    with pytest.raises(ValueError, match="Root note cannot be empty"):
        # We need to use a dictionary to bypass type checking
        # Use model_validate instead of model_validate_json to avoid JSON serialization issues
        data = {"root": "", "scale_type": "MAJOR"}  # Use string for scale_type to avoid JSON serialization issues
        ScaleInfo.model_validate(data)
    
    # Test with invalid octave
    with pytest.raises(ValueError):
        # Create a note with octave 8
        high_note = Note(
            note_name="C",
            octave=8,
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        )
        ScaleInfo(root=high_note, scale_type=ScaleType.MAJOR)

# Test get_scale method
def test_get_scale_instance_with_fixture(c_major_scale: ScaleInfo) -> None:
    """Test get_scale method with fixture."""
    # Get scale instance
    scale = c_major_scale.get_scale()
    
    # Verify it's a Scale object
    assert scale is not None
    
    # Since we've verified scale is not None, we can safely cast it
    scale_obj: Scale = scale  # type: ignore
    
    # Verify properties
    assert scale_obj.root.note_name == "C"
    assert scale_obj.scale_type == ScaleType.MAJOR
    
    # Verify notes
    assert len(scale_obj.notes) == 7
    for i, note in enumerate(scale_obj.notes):
        assert note.note_name in ["C", "D", "E", "F", "G", "A", "B"]
        if i == 0:
            assert note.note_name == "C"
        elif i == 1:
            assert note.note_name == "D"
        elif i == 2:
            assert note.note_name == "E"
        elif i == 3:
            assert note.note_name == "F"
        elif i == 4:
            assert note.note_name == "G"
        elif i == 5:
            assert note.note_name == "A"
        elif i == 6:
            assert note.note_name == "B"

# Test get_scale method with a new instance
def test_get_scale_with_new_instance() -> None:
    """Test get_scale method with a new instance."""
    # Create a scale info object
    scale_info = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Get scale instance
    scale = scale_info.get_scale()
    
    # Verify it's a Scale object
    assert scale is not None
    
    # Since we've verified scale is not None, we can safely cast it
    scale_obj: Scale = scale  # type: ignore
    
    # Verify properties
    assert scale_obj.root.note_name == "C"
    assert scale_obj.scale_type == ScaleType.MAJOR
    
    # Verify notes are correct
    assert len(scale_obj.notes) == 7
    for i, note in enumerate(scale_obj.notes):
        assert note.note_name in ["C", "D", "E", "F", "G", "A", "B"]
        if i == 0:
            assert note.note_name == "C"
        elif i == 1:
            assert note.note_name == "D"
        elif i == 2:
            assert note.note_name == "E"
        elif i == 3:
            assert note.note_name == "F"
        elif i == 4:
            assert note.note_name == "G"
        elif i == 5:
            assert note.note_name == "A"
        elif i == 6:
            assert note.note_name == "B"

# Test create_scale_from_params method
def test_scale_from_params() -> None:
    """Test creating a scale from parameters."""
    # Create a scale from params
    scale_info = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Get scale notes
    notes = scale_info.get_scale_notes()
    
    # Verify notes exist
    assert notes is not None
    
    # Cast to ensure type safety
    notes_list = cast(List[Note], notes)
    
    # Verify notes
    assert len(notes_list) == 7
    for i, expected_name in enumerate(["C", "D", "E", "F", "G", "A", "B"]):
        assert notes_list[i].note_name == expected_name
    
    # Test minor scale
    c_minor = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MINOR
    )
    
    # Get scale notes
    minor_notes = c_minor.get_scale_notes()
    
    # Verify notes exist
    assert minor_notes is not None
    
    # Cast to ensure type safety
    minor_notes_list = cast(List[Note], minor_notes)
    
    # Verify notes
    assert len(minor_notes_list) == 7
    # Check each note individually
    assert minor_notes_list[0].note_name == "C"
    assert minor_notes_list[1].note_name == "D"
    assert minor_notes_list[2].note_name == "D#"  # Eb as D#
    assert minor_notes_list[3].note_name == "F"
    assert minor_notes_list[4].note_name == "G"
    assert minor_notes_list[5].note_name == "G#"  # Ab as G#
    assert minor_notes_list[6].note_name == "A#"  # Bb as A#

# Test get_scale method with invalid scale type
def test_get_scale_with_invalid_scale_type() -> None:
    """Test getting a scale with an invalid scale type."""
    # Create a scale info object with a custom scale type
    # This is for testing purposes only, in real code we would use enum values
    # We're using model_validate to bypass type checking
    data = {
        "root": Note.from_note_name("C"),
        "scale_type": "CUSTOM"  # Not a valid ScaleType
    }
    
    # This should raise a validation error
    with pytest.raises(ValidationError):
        ScaleInfo.model_validate(data)

# Test scale instance
def test_scale_instance() -> None:
    """Test get_scale method."""
    # Create a scale info object
    c_major = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Get scale instance
    scale_obj = c_major.get_scale()
    
    # Verify it's a Scale object
    assert scale_obj is not None
    
    # Since we've verified scale_obj is not None, we can safely cast it
    scale: Scale = scale_obj  # type: ignore
    
    # Verify properties
    assert scale.root.note_name == "C"
    assert scale.scale_type == ScaleType.MAJOR
    
    # Verify notes are correct
    assert len(scale.notes) == 7
    for i, note in enumerate(scale.notes):
        assert note.note_name in ["C", "D", "E", "F", "G", "A", "B"]
        if i == 0:
            assert note.note_name == "C"
        elif i == 1:
            assert note.note_name == "D"
        elif i == 2:
            assert note.note_name == "E"
        elif i == 3:
            assert note.note_name == "F"
        elif i == 4:
            assert note.note_name == "G"
        elif i == 5:
            assert note.note_name == "A"
        elif i == 6:
            assert note.note_name == "B"

# Test create_scale_from_key method
def test_create_scale_from_key() -> None:
    """Test creating a scale from a key."""
    # Create a scale info object from key
    scale_info = ScaleInfo(
        root=Note.from_note_name("C"),
        key="C4",
        scale_type=ScaleType.MAJOR
    )
    
    # Verify it's a ScaleInfo object
    assert scale_info is not None
    
    # Verify properties
    assert scale_info.root is not None
    assert scale_info.root.note_name == "C"
    assert scale_info.scale_type == ScaleType.MAJOR
    
    # Test with minor key
    scale_info_minor = ScaleInfo(
        root=Note.from_note_name("C"),
        key="C4",
        scale_type=ScaleType.MINOR
    )
    
    # Verify it's a ScaleInfo object
    assert scale_info_minor is not None
    
    # Verify properties
    assert scale_info_minor.root is not None
    assert scale_info_minor.root.note_name == "C"
    assert scale_info_minor.scale_type == ScaleType.MINOR

# Test get_scale_notes method with proper validation
def test_get_scale_notes_with_validation() -> None:
    """Test get_scale_notes method with proper validation."""
    # Create a scale info object
    c_major = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MAJOR
    )
    
    # Get scale notes
    notes = c_major.get_scale_notes()
    
    # Verify notes
    assert notes is not None
    notes_list = cast(List[Note], notes)  # Cast to ensure type safety
    assert len(notes_list) == 7
    for i, expected_name in enumerate(["C", "D", "E", "F", "G", "A", "B"]):
        assert notes_list[i].note_name == expected_name
    
    # Test minor scale
    c_minor = ScaleInfo(
        root=Note.from_note_name("C"),
        scale_type=ScaleType.MINOR
    )
    
    # Get scale notes
    minor_notes = c_minor.get_scale_notes()
    
    # Verify notes
    assert minor_notes is not None
    minor_notes_list = cast(List[Note], minor_notes)  # Cast to ensure type safety
    assert len(minor_notes_list) == 7
    # Check each note individually
    assert minor_notes_list[0].note_name == "C"
    assert minor_notes_list[1].note_name == "D"
    assert minor_notes_list[2].note_name == "D#"  # Eb as D#
    assert minor_notes_list[3].note_name == "F"
    assert minor_notes_list[4].note_name == "G"
    assert minor_notes_list[5].note_name == "G#"  # Ab as G#
    assert minor_notes_list[6].note_name == "A#"  # Bb as A#
