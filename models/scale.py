"""Scale class for musical scales."""
from typing import Dict, List, Tuple, ClassVar, Any, Optional
from pydantic import BaseModel, Field, field_validator, computed_field

from .note import Note
from .scale_info import ScaleInfo  # Import ScaleInfo
from .scale_degree import ScaleDegree  # Import ScaleDegree

class Scale(BaseModel):
    """A musical scale."""
    root: Note
    quality: str = Field(default="major", description="The quality of the scale (e.g., major, minor)")
    notes: List[Note] = Field(default_factory=list)
    scale_degrees: List[ScaleDegree] = Field(default_factory=list)
    scale_info: Optional[ScaleInfo] = None

    # Scale patterns for different keys
    MAJOR_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "C": [("C",""), ("D",""), ("E",""), ("F",""), ("G",""), ("A",""), ("B","")],
        "G": [("G",""), ("A",""), ("B",""), ("C",""), ("D",""), ("E",""), ("F","#")],
        "D": [("D",""), ("E",""), ("F","#"), ("G",""), ("A",""), ("B",""), ("C","#")],
        "A": [("A",""), ("B",""), ("C","#"), ("D",""), ("E",""), ("F","#"), ("G","#")],
        "E": [("E",""), ("F","#"), ("G","#"), ("A",""), ("B",""), ("C","#"), ("D","#")],
        "B": [("B",""), ("C","#"), ("D","#"), ("E",""), ("F","#"), ("G","#"), ("A","#")],
        "F#": [("F","#"), ("G","#"), ("A","#"), ("B",""), ("C","#"), ("D","#"), ("E","#")],
        "C#": [("C","#"), ("D","#"), ("E","#"), ("F","#"), ("G","#"), ("A","#"), ("B","#")],
        "G#": [("G","#"), ("A","#"), ("B","#"), ("C","#"), ("D","#"), ("E","#"), ("F","##")],
        "F": [("F",""), ("G",""), ("A",""), ("B","b"), ("C",""), ("D",""), ("E","")],
        "Bb": [("B","b"), ("C",""), ("D",""), ("E","b"), ("F",""), ("G",""), ("A","")],
        "Eb": [("E","b"), ("F",""), ("G",""), ("A","b"), ("B","b"), ("C",""), ("D","")],
        "Ab": [("A","b"), ("B","b"), ("C",""), ("D","b"), ("E","b"), ("F",""), ("G","")],
        "Db": [("D","b"), ("E","b"), ("F",""), ("G","b"), ("A","b"), ("B","b"), ("C","")],
        "Gb": [("G","b"), ("A","b"), ("B","b"), ("C","b"), ("D","b"), ("E","b"), ("F","")]
    }

    MINOR_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "C": [("C",""), ("D",""), ("E","b"), ("F",""), ("G",""), ("A","b"), ("B","b")],
        "G": [("G",""), ("A",""), ("B","b"), ("C",""), ("D",""), ("E","b"), ("F","")],
        "D": [("D",""), ("E",""), ("F",""), ("G",""), ("A",""), ("B","b"), ("C","")],
        "A": [("A",""), ("B",""), ("C",""), ("D",""), ("E",""), ("F",""), ("G","")],
        "E": [("E",""), ("F","#"), ("G",""), ("A",""), ("B",""), ("C",""), ("D","")],
        "B": [("B",""), ("C","#"), ("D",""), ("E",""), ("F","#"), ("G",""), ("A","")],
        "F#": [("F","#"), ("G","#"), ("A",""), ("B",""), ("C","#"), ("D",""), ("E","")],
        "C#": [("C","#"), ("D","#"), ("E",""), ("F","#"), ("G","#"), ("A",""), ("B","")],
        "Bb": [("B","b"), ("C",""), ("D","b"), ("E","b"), ("F",""), ("G","b"), ("A","b")],
        "Eb": [("E","b"), ("F",""), ("G","b"), ("A","b"), ("B","b"), ("C","b"), ("D","b")]
    }

    HARMONIC_MINOR_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "A": [("A",""), ("B",""), ("C",""), ("D",""), ("E",""), ("F",""), ("G","#")],
        "E": [("E",""), ("F","#"), ("G",""), ("A",""), ("B",""), ("C",""), ("D","#")],
        "B": [("B",""), ("C","#"), ("D",""), ("E",""), ("F","#"), ("G",""), ("A","#")],
        "F#": [("F","#"), ("G","#"), ("A",""), ("B",""), ("C","#"), ("D",""), ("E","#")],
        "C#": [("C","#"), ("D","#"), ("E",""), ("F","#"), ("G","#"), ("A",""), ("B","#")],
        "G#": [("G","#"), ("A","#"), ("B",""), ("C","#"), ("D","#"), ("E",""), ("F","##")],
        "D": [("D",""), ("E",""), ("F",""), ("G",""), ("A",""), ("B","b"), ("C","#")],
        "G": [("G",""), ("A",""), ("B","b"), ("C",""), ("D",""), ("E","b"), ("F","#")],
        "C": [("C",""), ("D",""), ("E","b"), ("F",""), ("G",""), ("A","b"), ("B","")],
        "F": [("F",""), ("G",""), ("A","b"), ("B","b"), ("C",""), ("D","b"), ("E","")],
        "Bb": [("B","b"), ("C",""), ("D","b"), ("E","b"), ("F",""), ("G","b"), ("A","")],
        "Eb": [("E","b"), ("F",""), ("G","b"), ("A","b"), ("B","b"), ("C","b"), ("D","")]
    }

    MELODIC_MINOR_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "A": [("A",""), ("B",""), ("C",""), ("D",""), ("E",""), ("F","#"), ("G","#")],
        "E": [("E",""), ("F","#"), ("G",""), ("A",""), ("B",""), ("C","#"), ("D","#")],
        "B": [("B",""), ("C","#"), ("D",""), ("E",""), ("F","#"), ("G","#"), ("A","#")],
        "F#": [("F","#"), ("G","#"), ("A",""), ("B",""), ("C","#"), ("D","#"), ("E","#")],
        "D": [("D",""), ("E",""), ("F",""), ("G",""), ("A",""), ("B",""), ("C","#")],
        "G": [("G",""), ("A",""), ("Bb",""), ("C",""), ("D",""), ("E",""), ("F","#")],
        "C": [("C",""), ("D",""), ("Eb",""), ("F",""), ("G",""), ("A",""), ("B","")],
        "F": [("F",""), ("G",""), ("Ab",""), ("Bb",""), ("C",""), ("D",""), ("E","")],
        "Bb": [("Bb",""), ("C",""), ("Db",""), ("Eb",""), ("F",""), ("G",""), ("A","")]
    }

    MIXOLYDIAN_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "C": [("C",""), ("D",""), ("E",""), ("F",""), ("G",""), ("A",""), ("Bb","")],
        "G": [("G",""), ("A",""), ("B",""), ("C",""), ("D",""), ("E",""), ("F","")],
        "D": [("D",""), ("E",""), ("F","#"), ("G",""), ("A",""), ("B",""), ("C","")],
        "A": [("A",""), ("B",""), ("C","#"), ("D",""), ("E",""), ("F","#"), ("G","")],
        "E": [("E",""), ("F","#"), ("G","#"), ("A",""), ("B",""), ("C","#"), ("D","")],
        "B": [("B",""), ("C","#"), ("D","#"), ("E",""), ("F","#"), ("G","#"), ("A","")],
        "F": [("F",""), ("G",""), ("A",""), ("Bb",""), ("C",""), ("D",""), ("Eb","")],
        "Bb": [("Bb",""), ("C",""), ("D",""), ("Eb",""), ("F",""), ("G",""), ("Ab","")],
        "Eb": [("Eb",""), ("F",""), ("G",""), ("Ab",""), ("Bb",""), ("C",""), ("Db","")]
    }

    WHOLE_TONE_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "C": [("C",""), ("D",""), ("E",""), ("F","#"), ("G","#"), ("A","#")],
        "Db": [("Db",""), ("Eb",""), ("F",""), ("G",""), ("A",""), ("B","")],
        "D": [("D",""), ("E",""), ("F","#"), ("G","#"), ("A","#"), ("C","")],
        "Eb": [("Eb",""), ("F",""), ("G",""), ("A",""), ("B",""), ("Db","")],
        "E": [("E",""), ("F","#"), ("G","#"), ("A","#"), ("C",""), ("D","")],
        "F": [("F",""), ("G",""), ("A",""), ("B",""), ("C","#"), ("D","#")],
    }

    CHROMATIC_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "C": [("C",""), ("C","#"), ("D",""), ("D","#"), ("E",""), ("F",""), 
              ("F","#"), ("G",""), ("G","#"), ("A",""), ("A","#"), ("B","")],
        "G": [("G",""), ("G","#"), ("A",""), ("A","#"), ("B",""), ("C",""), 
              ("C","#"), ("D",""), ("D","#"), ("E",""), ("F",""), ("F","#")],
        "D": [("D",""), ("D","#"), ("E",""), ("F",""), ("F","#"), ("G",""), 
              ("G","#"), ("A",""), ("A","#"), ("B",""), ("C",""), ("C","#")],
        "A": [("A",""), ("A","#"), ("B",""), ("C",""), ("C","#"), ("D",""), 
              ("D","#"), ("E",""), ("F",""), ("F","#"), ("G",""), ("G","#")],
        "E": [("E",""), ("F",""), ("F","#"), ("G",""), ("G","#"), ("A",""), 
              ("A","#"), ("B",""), ("C",""), ("C","#"), ("D",""), ("D","#")],
    }

    AUGMENTED_SCALE_PATTERNS: ClassVar[Dict[str, List[Tuple[str, str]]]] = {
        "C": [("C",""), ("D","#"), ("E",""), ("G",""), ("A","b"), ("B",""), ("C","")],
        "D": [("D",""), ("E","#"), ("F","#"), ("A",""), ("B","b"), ("C","#"), ("D","")],
        "E": [("E",""), ("F","##"), ("G","#"), ("B",""), ("C",""), ("D","#"), ("E","")],
        "F": [("F",""), ("G","#"), ("A",""), ("C",""), ("D","b"), ("E",""), ("F","")],
        "G": [("G",""), ("A","#"), ("B",""), ("D",""), ("E","b"), ("F","#"), ("G","")],
        "A": [("A",""), ("B","#"), ("C","#"), ("E",""), ("F",""), ("G","#"), ("A","")],
        "B": [("B",""), ("C","##"), ("D","#"), ("F","#"), ("G",""), ("A","#"), ("B","")]
    }

    SCALE_INTERVALS: ClassVar[Dict[str, List[int]]] = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
        "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "locrian": [0, 1, 3, 5, 6, 8, 10],
        "whole_tone": [0, 2, 4, 6, 8, 10],
        "diminished": [0, 2, 3, 5, 6, 8, 9, 11],
        "augmented": [0, 3, 4, 7, 8, 11],
        "chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    }

    def __init__(self, **data: Any) -> None:
        """Initialize a scale."""
        super().__init__(**data)
        self.notes = self._build_scale_from_intervals()
        self.scale_degrees = self._get_scale_degrees()

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Convert the scale to a dictionary."""
        base_dict = super().model_dump(**kwargs)
        return {
            'root': self.root.model_dump(),
            'quality': self.quality,
            'notes': [note.model_dump() for note in self.notes],
            'scale_degrees': [degree.model_dump() for degree in self.scale_degrees],
            'scale_info': self.scale_info.model_dump() if self.scale_info else None
        }

    @property
    def scale_type(self) -> str:
        """Get the scale type."""
        if isinstance(self.scale_info, ScaleInfo):
            return self.scale_info.scale_type
        return "major"  # default

    @property
    def key_signature(self) -> str:
        """Get the key signature."""
        if isinstance(self.scale_info, ScaleInfo):
            return self.scale_info.key_signature
        return ""  # default

    def _get_scale_degrees(self) -> List[ScaleDegree]:
        """Generate the scale degrees for this scale."""
        scale_degrees: List[ScaleDegree] = []
        for i, note in enumerate(self.notes, start=1):
            scale_degrees.append(ScaleDegree(
                degree=i,
                note=note,
                scale=self
            ))
        return scale_degrees

    def get_scale_notes(self) -> List[Note]:
        """Get the notes in this scale."""
        return self.notes[:]

    def get_scale_degrees(self) -> List[ScaleDegree]:
        """Get the scale degrees in this scale."""
        return self.scale_degrees[:]

    def get_scale_degree(self, degree: int) -> Note:
        """Get the note at a specific scale degree (1-based indexing)."""
        if degree < 1:
            raise ValueError("Scale degree must be positive")
        
        scale_notes = self.get_scale_notes()
        # Convert to 0-based index and handle wrapping for degrees > 7
        index = (degree - 1) % len(scale_notes)
        return scale_notes[index]

    def get_note_from_scale_degree(self, scale_degree: int) -> Note:
        """Get a note from its scale degree."""
        if not (1 <= scale_degree <= len(self.notes)):
            raise ValueError(f"Invalid scale degree: {scale_degree}")
        return self.notes[scale_degree - 1]  # Convert to 0-based index

    def _get_scale_degree_name(self, degree: int) -> str:
        """Get the name of the scale degree."""
        # Define the natural note sequence
        NATURAL_NOTES = ["C", "D", "E", "F", "G", "A", "B"]
        
        # Find the root note's position in the natural note sequence
        root_idx = NATURAL_NOTES.index(self.root.name)
        
        # Calculate the scale degree note
        degree_idx = (root_idx + degree) % 7
        return NATURAL_NOTES[degree_idx]

    def _build_scale_from_intervals(self) -> List[Note]:
        """Build a scale from intervals."""
        def create_notes_from_pattern(pattern: List[Tuple[str, str]]) -> List[Note]:
            notes = []
            for item in pattern:
                if not isinstance(item, tuple) or len(item) != 2:
                    raise ValueError(f"Invalid pattern item: {item}. Expected tuple of (name, accidental)")
                name, acc = item
                if len(name) > 1 and (name[1] == 'b' or name[1] == '#'):
                    note_name = name[0]
                    accidental = name[1:]
                else:
                    note_name = name
                    accidental = acc
                notes.append(Note(name=note_name, accidental=accidental))
            return notes

        # First try to use predefined patterns
        if self.quality == "major" and self.root.note_name in self.MAJOR_SCALE_PATTERNS:
            pattern = self.MAJOR_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
        elif self.quality == "minor" and self.root.note_name in self.MINOR_SCALE_PATTERNS:
            pattern = self.MINOR_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
        elif self.quality == "harmonic_minor" and self.root.note_name in self.HARMONIC_MINOR_SCALE_PATTERNS:
            pattern = self.HARMONIC_MINOR_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
        elif self.quality == "melodic_minor" and self.root.note_name in self.MELODIC_MINOR_SCALE_PATTERNS:
            pattern = self.MELODIC_MINOR_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
        elif self.quality == "mixolydian" and self.root.note_name in self.MIXOLYDIAN_SCALE_PATTERNS:
            pattern = self.MIXOLYDIAN_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
        elif self.quality == "whole_tone" and self.root.note_name in self.WHOLE_TONE_SCALE_PATTERNS:
            pattern = self.WHOLE_TONE_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
        elif self.quality == "chromatic" and self.root.note_name in self.CHROMATIC_SCALE_PATTERNS:
            pattern = self.CHROMATIC_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
        elif self.quality == "augmented" and self.root.note_name in self.AUGMENTED_SCALE_PATTERNS:
            pattern = self.AUGMENTED_SCALE_PATTERNS[self.root.note_name]
            notes = create_notes_from_pattern(pattern)
            # For augmented scale, we need to handle the root note at the end specially
            return notes
        else:
            # If no predefined pattern exists, calculate from intervals
            intervals = self.SCALE_INTERVALS.get(self.quality, [])
            if not intervals:
                raise ValueError(f"Unknown scale quality: {self.quality}")

            # Start with the root note
            notes = [self.root]
            
            # Get the natural note sequence starting from root
            NATURAL_NOTES = ["C", "D", "E", "F", "G", "A", "B"]
            root_idx = NATURAL_NOTES.index(self.root.name)
            
            # Add notes based on intervals
            for interval in intervals[1:]:  # Skip root note since we already have it
                # Get the target MIDI note
                target_midi = self.root.midi_note + interval
                
                # Get the natural note name for this scale degree
                scale_degree = len(notes)  # 0-based index
                note_idx = (root_idx + scale_degree) % 7
                natural_name = NATURAL_NOTES[note_idx]
                
                # Try natural note first
                natural_note = Note(name=natural_name)
                diff = target_midi - natural_note.midi_note
                
                # For diminished scale, handle special cases
                if self.quality == "diminished" and scale_degree in [6, 7]:  # 7th and 8th notes
                    # Use A and B instead of double flats
                    if scale_degree == 6:  # 7th note
                        new_note = Note(name="A")
                    else:  # 8th note
                        new_note = Note(name="B")
                else:
                    # Determine accidental based on difference
                    if diff == 0:
                        new_note = natural_note
                    elif diff > 0:
                        # Need sharp(s)
                        if diff > 2:  # Avoid too many sharps
                            next_note_idx = (note_idx + 1) % 7
                            natural_name = NATURAL_NOTES[next_note_idx]
                            accidental = "b"
                        else:
                            accidental = "#" * diff
                        new_note = Note(name=natural_name, accidental=accidental)
                    else:
                        # Need flat(s)
                        if abs(diff) > 2:  # Avoid too many flats
                            prev_note_idx = (note_idx - 1) % 7
                            natural_name = NATURAL_NOTES[prev_note_idx]
                            accidental = "#"
                        else:
                            accidental = "b" * abs(diff)
                        new_note = Note(name=natural_name, accidental=accidental)
                
                notes.append(new_note)

        # Add the root note at the end, one octave higher
        root_copy = Note(
            name=self.root.name,
            accidental=self.root.accidental,
            octave=self.root.octave + 1
        )
        return notes + [root_copy]

    def get_notes(self) -> List[Note]:
        """Get the notes of the scale."""
        return self.notes

    @field_validator('quality')
    @classmethod
    def validate_quality(cls, v: str) -> str:
        """Validate scale quality."""
        if v not in cls.SCALE_INTERVALS:
            raise ValueError(f"Unknown scale quality: {v}")
        return v

    @property
    def notes_computed(self) -> List[Note]:
        """Get the notes in the scale."""
        return self.get_scale_notes()

    @property
    def scale_notes(self) -> List[Note]:
        """Get the notes of the scale."""
        return self.get_notes()

    @property
    def root_name(self) -> str:
        """Get the root note name as a string."""
        if not hasattr(self.root, 'note_name'):
            return str(self.root)
        note_name = self.root.note_name
        return str(note_name) if note_name is not None else ""

    @property
    def quality_str(self) -> str:
        """Get the quality as a string."""
        return str(self.quality) if self.quality is not None else ""

    @property
    def scale_info(self) -> ScaleInfo:
        """Get the scale info."""
        return ScaleInfo(root=self.root, scale_type=self.quality)

    def _get_scale_intervals(self) -> List[int]:
        """Get the intervals for the scale."""
        return self.SCALE_INTERVALS.get(self.quality, [])

    def get_scale_degree(self, degree: int) -> Note:
        """Get the note at a specific scale degree (1-based indexing)."""
        if degree < 1:
            raise ValueError("Scale degree must be positive")
        
        scale_notes = self.get_scale_notes()
        # Convert to 0-based index and handle wrapping for degrees > 7
        index = (degree - 1) % len(scale_notes)
        return scale_notes[index]

    def get_note_from_scale_degree(self, scale_degree: int) -> Note:
        """Get a note from its scale degree."""
        if not (1 <= scale_degree <= len(self.notes)):
            raise ValueError(f"Invalid scale degree: {scale_degree}")
        return self.notes[scale_degree - 1]  # Convert to 0-based index

    def _get_accidentals(self) -> Dict[str, List[Tuple[str, str]]]:
        """Get the accidentals for this scale."""
        accidental_map: Dict[str, List[Tuple[str, str]]] = {
            'C': [],
            'G': [('F', '#')],
            'D': [('F', '#'), ('C', '#')],
            'A': [('F', '#'), ('C', '#'), ('G', '#')],
            'E': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#')],
            'B': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#'), ('A', '#')],
            'F#': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#'), ('A', '#'), ('E', '#')],
            'C#': [('F', '#'), ('C', '#'), ('G', '#'), ('D', '#'), ('A', '#'), ('E', '#'), ('B', '#')],
            'F': [('B', 'b')],
            'Bb': [('B', 'b'), ('E', 'b')],
            'Eb': [('B', 'b'), ('E', 'b'), ('A', 'b')],
            'Ab': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b')],
            'Db': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b'), ('G', 'b')],
            'Gb': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b'), ('G', 'b'), ('C', 'b')],
            'Cb': [('B', 'b'), ('E', 'b'), ('A', 'b'), ('D', 'b'), ('G', 'b'), ('C', 'b'), ('F', 'b')]
        }
        return accidental_map
