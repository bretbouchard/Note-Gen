from __future__ import annotations

from typing import Optional, Union, Any, cast, ClassVar, List, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator, validator, root_validator
from .note import Note
from .scale import Scale
from src.note_gen.core.enums import ScaleType, ChordQuality

class ScaleInfo(BaseModel):
    """Scale information class."""
    
    type: Literal["real"] = "real"  # Add discriminator field as a Literal
    root: Note
    key: Optional[str] = None
    scale_type: ScaleType

    # Add this model_config for Pydantic v2 compatibility
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        validate_default=True
    )
    
    @field_validator('root', mode='before')
    @classmethod
    def validate_root(cls, v: Any) -> Note:
        """Convert string to Note."""
        if v is None:
            raise ValueError("Root note cannot be None")
        if isinstance(v, str):
            # Handle empty string
            if not v:
                raise ValueError("Root note cannot be empty")
            
            # Handle full note name with octave (e.g., "C4")
            if len(v) > 1 and v[1:].isdigit():
                try:
                    return Note.from_full_name(v)
                except ValueError as e:
                    raise ValueError(f"Invalid note: {str(e)}") from e
            # Handle just note name (e.g., "C")
            if v not in Note.NOTE_TO_SEMITONE:
                raise ValueError(f"Invalid note name: {v}")
            return Note(
                note_name=v,
                octave=4,  # Default to middle octave
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            )
        elif isinstance(v, Note):
            return v
        else:
            raise ValueError(f"Root must be a string or Note object, got {type(v)}")

    @field_validator('key', mode='before')
    @classmethod
    def validate_key(cls, v: Any) -> Optional[str]:
        """Validate key format."""
        if v is None:
            return None
        
        if not isinstance(v, str):
            raise ValueError("Key must be a string")
            
        # Validate key format (note_name + octave)
        if not Note.FULL_NOTE_REGEX.match(v):
            raise ValueError(f"Invalid key format: {v}. Expected format: NOTE_NAME + OCTAVE (e.g., 'C4')")
            
        # Validate note name using Note's validation
        try:
            Note.from_full_name(v)
        except ValueError as e:
            raise ValueError(f"Invalid note: {str(e)}") from e
            
        # Validate octave
        octave = int(v[-1])
        if octave < 0 or octave > 9:
            raise ValueError(f"Invalid octave: {octave}. Must be between 0 and 9")
            
        return v

    @field_validator('scale_type', mode='before')
    @classmethod
    def validate_scale_type(cls, v: Any) -> ScaleType:
        """Convert string to ScaleType."""
        if isinstance(v, str):
            try:
                return ScaleType[v.upper()]
            except KeyError:
                raise ValueError(f"Invalid scale type: {v}. Must be one of {[t.name for t in ScaleType]}")
        elif isinstance(v, ScaleType):
            return v
        else:
            raise ValueError(f"Scale type must be a string or ScaleType enum, got {type(v)}")

    @model_validator(mode='after')
    def sync_key_and_root(self) -> ScaleInfo:
        """Initialize root from key if not present in constructor, and vice versa."""
        # If root is set but key isn't, set key from root
        if not self.key and self.root:
            self.key = str(self.root)
        # If key is set but root isn't adequately set, set root from key
        elif self.key and not self.root:
            self.root = self.validate_root_from_key(self.key)
        return self
        
    def validate_root_from_key(self, key: str) -> Note:
        """Convert a key string to a Note object for the root."""
        # Handle full note name with octave (e.g., "C4")
        if len(key) > 1 and key[1:].isdigit():
            note_name = key[0]
            octave = int(key[1:])
            return Note(
                note_name=note_name,
                octave=octave,
                duration=1.0,
                position=0.0,
                velocity=64,
                stored_midi_number=None,
                scale_degree=None,
                prefer_flats=False
            )
        # Handle just note name (e.g., "C")
        return Note(
            note_name=key,
            octave=4,  # Default to middle octave
            duration=1.0,
            position=0.0,
            velocity=64,
            stored_midi_number=None,
            scale_degree=None,
            prefer_flats=False
        )
    
    def get_note_for_degree(self, degree: int) -> Note:
        """Get the note for a given scale degree."""
        if not isinstance(degree, int):
            raise TypeError("Degree must be an integer")
            
        if degree == 0:
            raise ValueError("Degree cannot be zero")
            
        # Calculate octave offset
        if degree > 0:
            octave_offset = (degree - 1) // 7
        else:
            octave_offset = (abs(degree) - 1) // 7 - 1
            
        # Get intervals based on scale type
        intervals = [0, 2, 4, 5, 7, 9, 11] if self.scale_type == ScaleType.MAJOR else [0, 2, 3, 5, 7, 8, 10]
        
        # Calculate semitones from root
        semitones = intervals[(abs(degree) - 1) % 7] + (octave_offset * 12)
        
        # Create new note with adjusted midi number
        base_midi = self.root.get_midi_number()
        new_midi = base_midi + semitones
        
        # Create note from midi number
        note = Note.from_midi_number(new_midi)
        
        # Adjust octave
        if degree > 0:
            note.octave = self.root.octave + octave_offset
        else:
            note.octave = self.root.octave + octave_offset
            
        return note

    def get_scale(self) -> Optional[Scale]:
        """
        Get the Scale object corresponding to this ScaleInfo.
        
        Returns:
            Scale: The scale object, or None if it cannot be created.
        """
        try:
            return Scale(root=self.root, scale_type=self.scale_type)
        except ImportError:
            return None
    
    def get_scale_notes(self) -> List[Note]:
        """Get all notes in the scale.
        
        Returns:
            List of Note objects representing the scale
        """
        # Major scale intervals (in semitones)
        major_intervals = [0, 2, 4, 5, 7, 9, 11]
        minor_intervals = [0, 2, 3, 5, 7, 8, 10]
        
        # Get the intervals based on scale type
        intervals = major_intervals if self.scale_type == ScaleType.MAJOR else minor_intervals
        
        # Base MIDI number for the root note
        base_midi = self.root.get_midi_number()
        
        # Create notes for each scale degree
        notes = []
        for i, interval in enumerate(intervals):
            midi_num = base_midi + interval
            note = Note.from_midi_number(midi_num)
            notes.append(note)
            
        return notes

    # Add MAJOR_SCALE_QUALITIES constant for compatibility
    MAJOR_SCALE_QUALITIES: ClassVar[List[ChordQuality]] = [
        ChordQuality.MAJOR,
        ChordQuality.MINOR, 
        ChordQuality.MINOR,
        ChordQuality.MAJOR,
        ChordQuality.MAJOR,
        ChordQuality.MINOR,
        ChordQuality.DIMINISHED
    ]
    
    # Add MINOR_SCALE_QUALITIES constant for compatibility
    MINOR_SCALE_QUALITIES: ClassVar[List[ChordQuality]] = [
        ChordQuality.MINOR,
        ChordQuality.DIMINISHED,
        ChordQuality.MAJOR,
        ChordQuality.MINOR,
        ChordQuality.MINOR,
        ChordQuality.MAJOR,
        ChordQuality.MAJOR
    ]
