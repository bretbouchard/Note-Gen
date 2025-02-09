"""Data structures for musical note patterns."""

from __future__ import annotations
from uuid import uuid4, UUID
from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import NotePatternData  # Importing from patterns.py
from src.note_gen.models.scale import Scale  # Importing Scale model

# Type aliases
DirectionType = Literal["forward", "backward", "random", "alternating"]
ApproachType = Literal["chromatic", "diatonic", "below", "above"]
NoteType = Union[Note, ScaleDegree, Chord]


class NotePattern(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Name is required"}}})
    notes: Optional[List[Note]] = Field(None, json_schema_extra={"error_messages": {"required": {"message": "Notes are required"}}})
    description: str = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Description is required"}}})
    tags: List[str] = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Tags are required"}}})
    complexity: Optional[float] = None
    data: NotePatternData
    duration: Union[float, int] = Field(..., description="Pattern duration")
    position: Union[float, int] = Field(..., description="Pattern position")
    velocity: Union[float, int]
    index: Optional[int] = None  # Index of the note pattern
    pattern_type: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_data(self.data)

    @field_validator('duration', 'position', 'velocity', 'name', 'description', 'tags')
    def validate_fields(cls, v, field):
        if v is None:
            raise ValueError(f'{field.field_name} is required')
        if field.field_name in ['tags'] and not v:
            raise ValueError(f'{field.field_name} must be a non-empty list')
        if not isinstance(v, (int, float, str, list)):
            raise ValueError(f'{field.field_name} must be a number, string or list')
        return v

    @field_validator('tags')
    def validate_tags(cls, v):
        if v is None:
            raise ValueError("Tags must be a non-empty list of strings")
        if isinstance(v, list) and not v:
            raise ValueError("Tags must be a non-empty list of strings")
        if not all(isinstance(i, str) for i in v):
            raise ValueError("Tags must be a list of strings")
        return v

    @field_validator('name', 'description')
    def validate_name_description(cls, v, field):
        if v is None:
            raise ValueError(f'{field.field_name} must not be None')
        return v

    class Config:
        from_attributes = True

    @classmethod
    def validate_data(cls, v: NotePatternData) -> None:
        """
        Validates the provided NotePatternData instance.
        """
        from pydantic import ValidationError
        print("validate_data method called")
        print(f"Validating data: {v}")
        if not isinstance(v, NotePatternData):
            print("Data is not a valid NotePatternData instance.")
            return  
        print(f"Checking if notes is None or empty: {v.notes}")
        if v.notes is None or (isinstance(v.notes, list) and len(v.notes) == 0):
            print("Notes is empty or None.")
            raise ValueError("Notes must not be empty or None.")
        if not isinstance(v.notes, list):
            print("Notes is not a list.")
            return  
        for note in v.notes:
            print(f"Validating note: {note}")
            if not isinstance(note, dict) or 'note_name' not in note or 'octave' not in note:
                print("Invalid note structure.")
                return  
        if not isinstance(v.intervals, list) or not all(isinstance(i, int) for i in v.intervals):
            print("Intervals are not valid.")
            return  
        if not isinstance(v.duration, (int, float)) or v.duration <= 0:
            print("Duration is not valid.")
            return  

    def instantiate_with_key_scale(self, key: str, scale_type: str) -> 'NotePattern':
        """
        Create a new instance of the pattern with actual notes based on key and scale.
        
        Args:
            key: The key to use (e.g., 'C', 'F#')
            scale_type: The scale type (e.g., 'MAJOR', 'MINOR')
            
        Returns:
            A new NotePattern instance with concrete notes
        """
        # Create scale for the given key
        root_note = Note(note_name=key, octave=4, duration=1.0, velocity=100)
        scale = Scale(root=root_note, scale_type=scale_type)
        
        # Convert pattern indices to actual notes
        pattern_indices = self.data.pattern if isinstance(self.data.pattern, list) else []
        new_notes = []
        
        for idx in pattern_indices:
            if isinstance(idx, int):
                # Get the note from scale based on index
                scale_pos = idx % len(scale.notes)
                octave_shift = idx // len(scale.notes)
                note = scale.notes[scale_pos]
                # Create new note with adjusted octave
                new_note = Note(
                    note_name=note.note_name,
                    octave=note.octave + octave_shift,
                    duration=self.duration,
                    velocity=self.velocity
                )
                new_notes.append(new_note)
        
        # Create new pattern instance with concrete notes
        return NotePattern(
            name=self.name,
            notes=new_notes,
            pattern_type=self.pattern_type,
            description=self.description,
            tags=self.tags,
            complexity=self.complexity,
            data=self.data,
            duration=self.duration,
            position=self.position,
            velocity=self.velocity
        )


class NotePatternResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID of the note pattern")
    name: str = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Name is required"}}}, description="Name of the note pattern")
    notes: Optional[List[Note]] = Field(None, json_schema_extra={"error_messages": {"required": {"message": "Notes are required"}}}, description="List of notes in the pattern")
    pattern_type: Optional[str] = Field(None, description="Type of pattern")
    description: str = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Description is required"}}}, description="Pattern description")
    tags: List[str] = Field(..., json_schema_extra={"error_messages": {"required": {"message": "Tags are required"}}}, description="Pattern tags")
    complexity: Optional[float] = Field(None, description="Pattern complexity")
    data: Optional[Union[NotePatternData, List[Union[int, List[int]]]]] = Field(default=None, description="Additional pattern data")
    is_test: Optional[bool] = Field(default=None, description="Test flag")