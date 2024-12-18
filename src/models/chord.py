from __future__ import annotations
import logging
from typing import TypeAlias, Literal, Any, Dict, List, Optional, Union, AbstractSet, Mapping, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.base_types import MusicalBase
from src.models.note import Note
from src.models.chord_base import ChordBase, CHORD_INTERVALS, CHORD_COUNT
from src.models.enums import ChordQualityType
from src.models.chord_quality import ChordQuality

if TYPE_CHECKING:
    from src.models.roman_numeral import RomanNumeral
    from src.models.scale import Scale

# Define Literal types for warnings and modes
Modes: TypeAlias = Literal['json', 'python']
Warnings: TypeAlias = Literal['none', 'warn', 'error']

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Chord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Optional[Note] = None
    quality: Optional[ChordQualityType] = None  # This is probably the issue
    bass: Optional[Note] = None
    chord_notes: List[Note] = Field(default_factory=list)
    duration: Optional[float] = None
    velocity: Optional[int] = None
    inversion: int = Field(default=0)
    notes: List[Note] = Field(default_factory=list)  # Changed from _notes to notes

    @field_validator('quality')
    @classmethod
    def validate_quality(cls, value: Optional[Union[ChordQualityType, ChordQuality]]) -> ChordQualityType:
        """Validate chord quality."""
        if value is None:
            return ChordQualityType.MAJOR
        if isinstance(value, ChordQualityType):
            return value
        if isinstance(value, ChordQuality):
            return value.quality
        raise ValueError("Quality must be an instance of ChordQuality or ChordQualityType")

    def __init__(
        self,
        root: Note,
        quality: Union[ChordQuality, ChordQualityType],
        notes: Optional[List[Note]] = None,
        bass: Optional[Note] = None,
        inversion: int = 0,
        **kwargs: Any
    ) -> None:
        if not isinstance(root, Note):
            raise ValueError("Root must be a Note instance")
        if not isinstance(quality, (ChordQuality, ChordQualityType)):
            raise ValueError("Quality must be a ChordQuality or ChordQualityType instance")
        
        # Initialize with default values first
        super().__init__(
            root=root,
            quality=quality,
            bass=bass,
            inversion=inversion,
            **kwargs
        )
        
        # Initialize notes
        if notes is not None:
            if len(notes) == 0:
                raise ValueError("Notes cannot be empty")
            self.chord_notes = notes.copy()
        else:
            self.chord_notes = self._initialize_chord_notes(root, quality, inversion)
            if len(self.chord_notes) == 0:
                raise ValueError("Chord notes cannot be empty")
        
        # Apply inversion to get the final notes list
        self.notes = self._apply_inversion(self.chord_notes, self.inversion)

    def transpose(self, semitones: int) -> 'Chord':
        """Transpose the chord by the given number of semitones."""
        if not isinstance(self.root, Note):
            raise ValueError("Root note cannot be None")
        if not isinstance(self.quality, (ChordQuality, ChordQualityType)):
            raise ValueError("Quality must be a ChordQuality or ChordQualityType instance")
            
        new_root = Note.from_midi(self.root.midi_number + semitones)
        new_notes = [Note.from_midi(note.midi_number + semitones) for note in self.chord_notes]
        return Chord(
            root=new_root,
            quality=self.quality,  # This is now guaranteed to be non-None
            notes=new_notes,
            inversion=self.inversion
        )

    def generate_chord_notes(self, root: Note, quality: Union[ChordQuality, ChordQualityType], inversion: int) -> List[Note]:
        """Generate notes for a chord based on root, quality and inversion."""
        return self._initialize_chord_notes(root, quality, inversion)

    @classmethod
    def from_base(cls, base: ChordBase) -> 'Chord':
        """Create a chord from a ChordBase instance."""
        if not isinstance(base, ChordBase):
            raise ValueError("Invalid base: must be a ChordBase instance")
        
        if not isinstance(base.root, Note):
            raise ValueError("Base root must be a Note object")
        
        root_note = Note.from_midi(base.root.midi_number)
        notes = [Note.from_midi(base.root.midi_number + interval) for interval in base.intervals]
        
        quality = base.quality if hasattr(base, 'quality') else ChordQualityType.MAJOR
        
        return cls(
            root=base.root,
            quality=quality,  # Use the ChordQualityType directly
            notes=notes,
            inversion=0
        )

    def _apply_inversion(self, notes: List[Note], inversion: int) -> List[Note]:
        """Apply inversion to the chord notes."""
        if not notes:
            return notes
        
        effective_inversion = inversion % len(notes)
        if effective_inversion == 0:
            return notes.copy()
        
        inverted_notes = notes.copy()
        for _ in range(effective_inversion):
            first_note = inverted_notes.pop(0)
            inverted_notes.append(first_note)
        
        return inverted_notes


    def _initialize_chord_notes(self, root: Note, quality: Union[ChordQuality, ChordQualityType], inversion: int) -> List[Note]:
        """Initialize chord notes based on root and quality."""
        if not isinstance(root, Note):
            raise ValueError("Root must be a Note instance")
        if not isinstance(quality, (ChordQuality, ChordQualityType)):
            raise ValueError("Quality must be a ChordQuality or ChordQualityType instance")
        
        quality_type = quality.quality if isinstance(quality, ChordQuality) else quality
    
        # Rest of the method remains the same

        if quality_type == ChordQualityType.MAJOR:
            return [
                root,
                Note(name='E', octave=root.octave),  # Major third
                Note(name='G', octave=root.octave)   # Perfect fifth
            ]
        elif quality_type == ChordQualityType.MINOR:
            return [
                root,
                Note(name='D', octave=root.octave),  # Minor third
                Note(name='G', octave=root.octave)   # Perfect fifth
            ]
        elif quality_type == ChordQualityType.DIMINISHED:
            return [
                root,
                Note(name='D#', octave=root.octave),  # Diminished third
                Note(name='F#', octave=root.octave)   # Diminished fifth
            ]
        else:
            raise ValueError(f"Unsupported chord quality: {quality}")

Chord.model_rebuild()

# Example instantiation for testing