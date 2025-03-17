import pytest
from typing import Optional
from pydantic import ValidationError
from src.note_gen.models.patterns import NotePattern, NotePatternData
from src.note_gen.models.note import Note

def test_create_note_pattern() -> None:
    """Test creating a valid note pattern."""
    notes = [
        Note(note_name="C", octave=4),
        Note(note_name="E", octave=4),
        Note(note_name="G", octave=4)
    ]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    pattern = NotePattern(
        name='TestPattern',
        description='Test pattern description',
        tags=['valid_tag'],
        complexity=0.5,
        intervals=[0, 2, 4],
        data=pattern_data
    )
    assert pattern.name == 'TestPattern'
    assert pattern.intervals == [0, 2, 4]

def test_name_validation() -> None:
    """Test name validation rules."""
    # Test valid names
    notes = [Note(note_name="C", octave=4)]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    NotePattern(
        name="Valid Pattern",
        description="Valid pattern description",
        tags=['valid_tag'],
        complexity=0.5,
        intervals=[0, 2, 4],
        data=pattern_data
    )

    # Test invalid names
    with pytest.raises(ValidationError, match="String should have at least 2 characters"):
        NotePattern(
            name="A",
            description="Invalid pattern description",
            tags=['valid_tag'],
            complexity=0.5,
            intervals=[0, 2, 4],
            data=pattern_data
        )

def test_pattern_validation() -> None:
    """Test pattern validation rules."""
    # Test valid pattern
    notes = [Note(note_name="C", octave=4)]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    NotePattern(
        name="Valid Pattern",
        description="Valid pattern description",
        tags=['valid_tag'],
        complexity=0.5,
        intervals=[0, 2, 4],
        data=pattern_data
    )

    # Test invalid pattern
    with pytest.raises(ValidationError, match="Either intervals or notes must be provided"):
        # Create a pattern with empty intervals and no notes
        empty_notes: list[Note] = []
        empty_data = NotePatternData(notes=empty_notes, intervals=[])
        NotePattern(
            name="Invalid Pattern",
            description="Invalid pattern description",
            tags=['valid_tag'],
            complexity=0.5,
            intervals=[],
            data=empty_data
        )

def test_complexity_validation() -> None:
    """Test complexity validation rules."""
    # Test valid complexity
    notes = [Note(note_name="C", octave=4)]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    NotePattern(
        name="Valid Pattern",
        description="Valid pattern description",
        tags=['valid_tag'],
        complexity=0.5,
        intervals=[0, 2, 4],
        data=pattern_data
    )

    # Test invalid complexity
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        NotePattern(
            name="Invalid Pattern",
            description="Invalid pattern description",
            tags=['valid_tag'],
            complexity=1.5,
            intervals=[0, 2, 4],
            data=pattern_data
        )

def test_tags_validation() -> None:
    """Test tags validation rules."""
    # Test valid tags
    notes = [Note(note_name="C", octave=4)]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    NotePattern(
        name="Valid Pattern",
        description="Valid pattern description",
        tags=['valid_tag', 'another_tag'],
        complexity=0.5,
        intervals=[0, 2, 4],
        data=pattern_data
    )

    # Test invalid tags - using None which should be caught by validation
    with pytest.raises(ValidationError, match="Input should be a valid list"):
        NotePattern(
            name="Invalid Pattern",
            description="Invalid pattern description",
            tags=None,  # None should trigger validation error
            complexity=0.5,
            intervals=[0, 2, 4],
            data=pattern_data
        )

def test_add_remove_tag() -> None:
    """Test add_tag and remove_tag methods."""
    notes = [Note(note_name="C", octave=4)]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    pattern = NotePattern(
        name="Test Pattern",
        description="Test pattern description",
        tags=['initial_tag'],
        complexity=0.5,
        intervals=[0, 2, 4],
        data=pattern_data
    )

    pattern.add_tag('new_tag')
    assert 'new_tag' in pattern.tags

    pattern.remove_tag('initial_tag')
    assert 'initial_tag' not in pattern.tags

def test_invalid_data() -> None:
    """Test that creating a NotePattern with invalid data raises an error."""
    notes = [Note(note_name="C", octave=4)]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        NotePattern(
            name="Invalid Pattern",
            description="Test invalid pattern",
            tags=["test"],
            complexity=1.5,
            intervals=[0, 2, 4],
            data=pattern_data
        )

def test_note_pattern_empty_data() -> None:
    """Test creating a NotePattern with empty data."""
    notes = [Note(note_name="C", octave=4)]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 2, 4])
    
    pattern = NotePattern(
        name="Empty Data Pattern",
        description="Test empty data pattern",
        tags=["test"],
        complexity=0.5,
        intervals=[0, 2, 4],
        data=pattern_data
    )
    assert pattern.data is not None

def test_note_pattern_with_notes() -> None:
    """Test creating a NotePattern with notes."""
    notes = [
        Note(note_name="C", octave=4),
        Note(note_name="E", octave=4),
        Note(note_name="G", octave=4)
    ]
    pattern_data = NotePatternData(notes=notes, intervals=[0, 4, 7])
    pattern = NotePattern(
        name="Note Pattern",
        description="Test note pattern",
        tags=["test"],
        complexity=0.5,
        intervals=[0, 4, 7],
        data=pattern_data
    )
    assert len(pattern.get_notes()) == 3
    assert pattern.get_notes()[0].note_name == "C"

def test_note_pattern_with_invalid_intervals() -> None:
    """Test creating a NotePattern with invalid intervals."""
    notes = [Note(note_name="C", octave=4)]
    
    with pytest.raises(ValidationError, match="Input should be a valid integer"):
        invalid_data = {"notes": notes, "intervals": [0, "X", 4]}
        NotePattern(
            name="Invalid Intervals Pattern",
            description="Test invalid intervals pattern",
            tags=["test"],
            complexity=0.5,
            intervals=[0, "X", 4],
            data=invalid_data
        )