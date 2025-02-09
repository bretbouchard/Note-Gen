from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import logging

from src.note_gen.models.note import Note
from src.note_gen.models.enums import ChordQualityType

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chord(BaseModel):
    root: Note
    quality: ChordQualityType = ChordQualityType.MAJOR
    notes: List[Note] = []
    inversion: int = 0
    class Config:
        arbitrary_types_allowed = True

    @field_validator('root')
    @classmethod
    def validate_root(cls, root):
        logger.debug(f"Validating root: {root}")
        if not isinstance(root, Note):
            raise ValueError('Root must be a Note instance.')
        return root

    @field_validator('quality')
    @classmethod
    def validate_quality(cls, v: Union[str, ChordQualityType]) -> ChordQualityType:
        """Validate and convert the quality field."""
        if isinstance(v, str):
            try:
                # Try to convert string to ChordQualityType
                return ChordQualityType(v.upper())
            except ValueError:
                # Handle aliases
                aliases = {
                    'maj7': ChordQualityType.MAJOR7,
                    'maj': ChordQualityType.MAJOR,
                    'min': ChordQualityType.MINOR,
                    'dim': ChordQualityType.DIMINISHED,
                    'aug': ChordQualityType.AUGMENTED,
                    'dom7': ChordQualityType.DOMINANT7,
                    'm7': ChordQualityType.MINOR7,
                    'dim7': ChordQualityType.DIMINISHED7,
                }
                normalized = v.lower()
                if normalized in aliases:
                    return aliases[normalized]
                raise ValueError(f"Invalid chord quality: {v}")
        return v

    @field_validator('inversion')
    @classmethod
    def validate_inversion(cls, v: int) -> int:
        """Validate the inversion value."""
        if v < 0:
            raise ValueError("Inversion cannot be negative")
        return v

    @model_validator(mode='after')
    def generate_notes(self) -> 'Chord':
        """Generate the notes for this chord after validation."""
        if not self.notes:  # Only generate if notes are empty
            self.notes = self._generate_chord_notes()
            
        # Apply inversion if needed
        if self.inversion > 0:
            for _ in range(self.inversion):
                first_note = self.notes.pop(0)
                first_note = first_note.transpose(12)  # Move up an octave
                self.notes.append(first_note)
                
        return self

    def _generate_chord_notes(self) -> List[Note]:
        """Generate the notes that make up this chord."""
        if not self.root:  
            raise ValueError("Root note cannot be None.")

        if self.quality is None:
            raise ValueError("Chord quality cannot be None.")

        logger.info("Generating notes for chord...")
        intervals = self._get_intervals_for_quality()
        notes = []
        
        # Add root note
        notes.append(self.root)
        
        # Add other notes based on intervals
        for interval in intervals[1:]:  # Skip first interval (0) as it's the root
            note_params = self._calculate_note_for_interval(interval)
            note = Note(**note_params)
            notes.append(note)
            
        logger.debug(f"Generated notes before returning: {[{'name': note.note_name, 'octave': note.octave, 'duration': note.duration, 'velocity': note.velocity, 'midi_number': note.midi_number} for note in notes]}")
        return notes

    def _get_intervals_for_quality(self) -> List[int]:
        """Get the intervals for the chord quality."""
        quality_intervals = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
            ChordQualityType.MAJOR7: [0, 4, 7, 11],  # Major 7th chord intervals
            ChordQualityType.MINOR7: [0, 3, 7, 10],
            ChordQualityType.DOMINANT7: [0, 4, 7, 10],
            ChordQualityType.DIMINISHED7: [0, 3, 6, 9],
            ChordQualityType.HALF_DIMINISHED7: [0, 3, 6, 10],
            ChordQualityType.AUGMENTED7: [0, 4, 8, 10],
            ChordQualityType.SUS2: [0, 2, 7],
            ChordQualityType.SUS4: [0, 5, 7],
            ChordQualityType.SEVEN_SUS4: [0, 5, 7, 10],
        }
        return quality_intervals.get(self.quality, [0, 4, 7])  # Default to major triad intervals

    def _calculate_note_for_interval(self, interval: int) -> Dict[str, Any]:
        """Calculate the note parameters for a given interval from the root."""
        root_midi = self.root.midi_number
        new_midi = root_midi + interval
        
        # Calculate octave and note name
        octave = (new_midi // 12) - 1  # MIDI note 60 is middle C (C4)
        note_number = new_midi % 12
        
        # Use the Note class's preferred note names for consistency
        note_name = Note.SEMITONE_TO_NOTE[note_number]
        
        return {
            'note_name': note_name,
            'octave': octave,
            'duration': self.root.duration,
            'velocity': self.root.velocity
        }

    def get_notes(self) -> List[Note]:
        logger.info("Getting notes for chord...")  
        return self.generate_notes()

    @classmethod
    def from_string(cls, chord_str: str) -> 'Chord':
        """Create a Chord from a string representation (e.g., 'C', 'Dm', 'G7')."""
        root_end = 1
        if len(chord_str) > 1 and chord_str[1] in ['#', 'b']:
            root_end = 2
        root_str = chord_str[:root_end]
        
        quality = ChordQualityType.MAJOR
        
        if len(chord_str) > root_end:
            quality_str = chord_str[root_end:]
            try:
                quality = ChordQualityType.from_string(quality_str)
            except ValueError:
                raise ValueError(f"Invalid quality string: {quality_str}")
        
        root = Note(note_name=root_str, octave=4)
        
        return cls(root=root, quality=quality)

    @classmethod
    def from_quality(cls, root: Note, quality: str) -> 'Chord':
        """Create a chord from a root note and quality string."""
        quality_type = ChordQualityType.from_string(quality)
        chord = cls(root=root, quality=quality_type)
        logger.debug(f"Calling generate_notes for chord: root={root.note_name}, quality={quality}")
        chord.generate_notes()  
        logger.debug(f"Chord created with root: {root.note_name}, quality: {quality}")
        logger.debug(f"Chord notes after generation: {chord.notes}")
        return chord

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the given number of semitones."""
        new_root = self.root.transpose(semitones)
        return Chord(root=new_root, quality=self.quality, inversion=self.inversion)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'root': self.root,
            'quality': self.quality,
            'notes': [note.to_dict() for note in self.notes] if self.notes is not None else None,
            'inversion': self.inversion
        }

    def to_json(self) -> dict:
        return {
            'root': self.root.to_json(),  
            'quality': self.quality,
            'notes': [note.to_json() for note in self.notes] if self.notes else [],
            'inversion': self.inversion
        }

    def some_function(self) -> None:
        pass

    def another_function(self) -> None:
        if self.notes is not None:
            for note in self.notes:
                print(note.to_dict())  
        else:
            print("No notes available")

    def interpret_chord_symbol(self, chord_symbol: str, key: str, scale_type: str) -> Note:
        note_map = {
            'I': Note(note_name='C', octave=4),
            'ii': Note(note_name='D', octave=4),
            'iii': Note(note_name='E', octave=4),
            'IV': Note(note_name='F', octave=4),
            'V': Note(note_name='G', octave=4),
            'vi': Note(note_name='A', octave=4),
            'vii°': Note(note_name='B', octave=4),
        }
        return note_map.get(chord_symbol, Note(note_name='C', octave=4))  

class MockDatabase:
    def __init__(self):
        self.data = []

    async def insert(self, pattern):
        self.data.append(pattern)
