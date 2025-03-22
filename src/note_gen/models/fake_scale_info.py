from typing import Literal, Dict, List, Optional, Any, ClassVar, TYPE_CHECKING, Union
from pydantic import BaseModel, ConfigDict, field_validator, validator
from .note import Note
from src.note_gen.core.enums import ScaleType

# Import ChordQuality only when type checking
if TYPE_CHECKING:
    from .chord import ChordQuality

class BaseScaleInfo(BaseModel):
    """Base scale information model."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    
    type: str

"""Fake scale info for testing purposes."""

class FakeScaleInfo(BaseScaleInfo):
    """Fake scale information class for testing."""
    
    type: Literal["fake"] = "fake"
    root: Note
    scale_type: ScaleType
    key: str
    complexity: float = 0.5
    
    # Add this model_config for Pydantic v2 compatibility
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    
    @field_validator('root', mode='before')
    @classmethod
    def validate_root(cls, v: Any) -> Note:
        """Convert string to Note object."""
        if isinstance(v, str):
            try:
                return Note(
                    note_name=v, 
                    octave=4,  # Default octave
                    duration=0.0,
                    position=0.0,
                    velocity=0,
                    stored_midi_number=None,
                    scale_degree=None,
                    prefer_flats=False
                )
            except ValueError:
                raise ValueError(f"Invalid root note: {v}")
        if isinstance(v, Note):
            return v
        raise ValueError(f"Invalid root note type: {type(v)}")
    
    @field_validator('scale_type', mode='before')
    @classmethod
    def validate_scale_type(cls, v: Any) -> ScaleType:
        """Convert string to ScaleType enum."""
        if isinstance(v, str):
            try:
                return ScaleType(v.upper())
            except ValueError:
                raise ValueError(f"Invalid scale type: {v}")
        if isinstance(v, ScaleType):
            return v
        raise ValueError(f"Invalid scale type: {v}")

    def get_note_for_degree(self, degree: int) -> Note:
        """Get the note for a given scale degree."""
        # Map negative degrees to the same note at an octave below:
        # e.g., if degree = -1, return degree = 7 at octave - 1
        # Used for testing
        if degree < 1:
            # degree should be 1, 2, 3...
            # so if we have degree = -1, we want 7
            # if we have degree = 0, we want 8 (octave)
            # if we have degree = -2, we want 6
            # if we have degree = -7, we want 1, octave -= 1
            # if we have degree = -8, we want 8, octave -= 1
            # We can do this by taking (degree % 7)
            # but if result is 0, we need 7
            # so we do ((degree - 1) % 7) + 1
            transformed_degree = ((degree - 1) % 7) + 1
            octave_change = (degree - 1) // 7  # How many octaves to lower
            # Make a new note with the same name but lower octave
            new_note = Note(
                note_name=self.root.note_name,
                octave=self.root.octave + octave_change,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            )
            return new_note
        return self.root
    
    # Add MAJOR_SCALE_QUALITIES constant for compatibility
    MAJOR_SCALE_QUALITIES: ClassVar[List[str]] = [
        "MAJOR",
        "MINOR", 
        "MINOR",
        "MAJOR",
        "MAJOR",
        "MINOR",
        "DIMINISHED"
    ]
    
    # Add MINOR_SCALE_QUALITIES constant for compatibility
    MINOR_SCALE_QUALITIES: ClassVar[List[str]] = [
        "MINOR",
        "DIMINISHED",
        "MAJOR",
        "MINOR",
        "MINOR",
        "MAJOR",
        "MAJOR"
    ]

    def get_scale_notes(self) -> List[Note]:
        """Get all notes in the scale.
        
        Returns:
            List of Note objects representing the scale
        """
        # Create a simple list of 7 notes based on the root note
        # This is a simplified version for testing purposes
        notes = []
        
        # Create the root note
        notes.append(self.root)
        
        # Create 6 additional fake notes to represent the rest of the scale
        # In a real implementation, these would be calculated based on scale intervals
        for i in range(1, 7):
            note = Note(
                note_name=self.root.note_name,  # All notes have same name for simplicity
                octave=self.root.octave,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=i + 1,  # Scale degree increases for each note
                prefer_flats=False
            )
            notes.append(note)
            
        return notes

# Rebuild the model to finalize forward references
FakeScaleInfo.model_rebuild()

class RealScaleInfo(BaseScaleInfo):
    """Real scale info."""
    type: Literal["real"] = "real"
    root: Note
    scale_type: ScaleType
    key: str

    model_config = ConfigDict(
        discriminator="type",
        json_schema_extra={
            "examples": [
                {"type": "real", "root": "C", "scale_type": "major", "key": "C major"},
                {"type": "fake", "root": "C", "scale_type": "major", "key": "C major", "complexity": 0.5}
            ]
        }
    )
