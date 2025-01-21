from __future__ import annotations
from typing import List, Dict, ClassVar, Optional
import random
import logging
from pydantic import BaseModel, ValidationError, Field

from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord_quality import ChordQualityType
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.enums import ScaleType

logger = logging.getLogger(__name__)

class ScaleInfo(BaseModel):
    """Base class for scale information."""
    
    root: Note
    scale_type: ScaleType

    def get_chord_quality_for_degree(self, degree: int) -> ChordQualityType:
        """Return the chord quality for a given degree."""
        # Logic to return chord quality based on degree
        pass

class ProgressionGenerator(BaseModel):
    """Base class for chord progressions."""
    
    name: str
    chords: List[Chord]
    key: str
    scale_type: ScaleType

    def example_method(self) -> None:
        """Example method with proper return type and annotations."""
        pass

class ChordProgressionGenerator(BaseModel):
    """Generator for creating chord progressions."""
    
    scale_info: ScaleInfo
    # Mapping from integers to Roman numerals
    INT_TO_ROMAN: ClassVar[Dict[int, str]] = {
        1: "I",
        2: "II",
        3: "III",
        4: "IV",
        5: "V",
        6: "VI",
        7: "VII"
    }
    
    def generate(self, pattern: Optional[List[str]] = None, progression_length: Optional[int] = None) -> ChordProgression:
        """Generate a chord progression based on a pattern or length."""
        if pattern is None and progression_length is None:
            raise ValueError("Must provide either a pattern or a progression_length")
            
        if progression_length is not None and progression_length <= 0:
            raise ValueError("progression_length must be positive")

        if pattern is not None:
            # Handle empty pattern case
            if not pattern:
                raise ValueError("Pattern list cannot be empty")
                
            # Split each pattern string into individual numerals
            expanded_pattern = []
            for p in pattern:
                expanded_pattern.extend(p.split('-'))
            
            # If progression_length is specified, repeat the pattern
            if progression_length is not None:
                pattern_length = len(expanded_pattern)
                repetitions = progression_length // pattern_length
                remainder = progression_length % pattern_length
                expanded_pattern = expanded_pattern * repetitions + expanded_pattern[:remainder]
                
            return self.generate_from_pattern(expanded_pattern)
        else:
            if progression_length is None:
                raise ValueError("progression_length must be provided and cannot be None")
            return self.generate_random(length=progression_length)

    def generate_random(self, length: int) -> ChordProgression:
        """Generate a random chord progression of specified length."""
        if length <= 0:
            raise ValueError("Length must be positive")
            
        # Generate random progression
        pattern = []
        for _ in range(length):
            degree = random.choice(list(self.INT_TO_ROMAN.keys()))  # Choose a random scale degree (1-7)
            quality = random.choice(["major", "minor"])  # Choose a random quality
            numeral = self.INT_TO_ROMAN[degree]
            if quality == "minor":
                numeral = numeral.lower()
            pattern.append(numeral)
            
        return self.generate_from_pattern(pattern)
    
    def convert_roman_to_chord(self, numeral: str) -> Chord:
        roman = RomanNumeral.from_string(numeral)  # Convert numeral to scale degree
        root = self.scale_info.root  # Get root note
        quality = self.scale_info.get_chord_quality_for_degree(roman.scale_degree)  # Get quality from scale
        return Chord(root=root, quality=quality)  # Create Chord instance

    def generate_from_pattern(self, pattern: List[str]) -> ChordProgression:
        """Generate a chord progression from a pattern of Roman numerals."""
        chords = []
        for numeral in pattern:
            try:
                roman = RomanNumeral.from_string(numeral)  # Create RomanNumeral instance
                root = self.scale_info.root  # Get scale degree as integer
                chord = self.generate_chord(numeral)
                chords.append(chord)  # Append the Chord instance directly
            except (ValueError, ValidationError) as e:
                raise ValueError(f"Invalid Roman numeral in pattern: {numeral}") from e

        return ChordProgression(name="Generated Progression", chords=chords, key=self.scale_info.root.note_name, scale_type=self.scale_info.scale_type)
    
    def generate_chord(self, roman_numeral: str) -> Chord:
        """Generate a chord from a Roman numeral."""
        try:
            roman = RomanNumeral.from_string(roman_numeral)
            root = self.scale_info.root
            # Get quality from scale_info
            quality = self.scale_info.get_chord_quality_for_degree(roman.scale_degree)
            if root is None:
                raise ValueError(f"Root note for {roman_numeral} cannot be None")
            if quality is None:
                raise ValueError(f"Quality for {roman_numeral} cannot be None")
            chord = Chord(root=root, quality=quality)
            return chord  # Return the Chord instance directly
        except (ValueError, ValidationError) as e:
            raise ValueError(f"Invalid Roman numeral: {roman_numeral}") from e
        
    def generate_chord_notes(self, root: Note, quality: ChordQualityType, inversion: int = 0) -> List[Note]:
        """Generate the notes for a chord based on root, quality, and inversion."""
        # Generate base chord notes
        if quality == ChordQualityType.MAJOR:
            notes = [root, root.transpose(4), root.transpose(7)]  # Root, Major 3rd, Perfect 5th
        elif quality == ChordQualityType.MINOR:
            notes = [root, root.transpose(3), root.transpose(7)]  # Root, Minor 3rd, Perfect 5th
        elif quality == ChordQualityType.DOMINANT_7:
            notes = [root, root.transpose(4), root.transpose(7), root.transpose(10)]  # Root, Major 3rd, Perfect 5th, Minor 7th
        else:
            raise ValueError(f"Unsupported chord quality: {quality}")

        # Handle inversions
        if inversion > 0:
            # Rotate the notes based on inversion number
            for _ in range(inversion):
                first_note = notes.pop(0)
                # Move the first note up an octave
                notes.append(first_note.transpose(12))

        return notes
    
    def generate_custom(self, degrees: List[int], qualities: List[str]) -> ChordProgression:
        """Generate a chord progression with custom degrees and qualities."""
        if len(degrees) != len(qualities):
            raise ValueError("Number of degrees must match number of qualities")
            
        chords = []
        for degree, quality in zip(degrees, qualities):
            # Convert degree to Roman numeral
            roman = self.INT_TO_ROMAN[degree]
            if quality.lower() == "minor":
                roman = roman.lower()
            elif quality.lower() == "diminished":
                roman = roman.lower() + "o"
            elif quality.lower() == "augmented":
                roman = roman + "+"
            
            chord = self.generate_chord(roman)
            chords.append(chord)  # Append the Chord instance directly
            
        return ChordProgression(name="Custom Progression", chords=chords, key=self.scale_info.root.note_name, scale_type=self.scale_info.scale_type)

class FakeScaleInfo(ScaleInfo):
    def __init__(self, root: Note = None, scale_type: ScaleType = ScaleType.MAJOR, key: str = 'C'):
        super().__init__(root or Note(note_name='C', octave=4, duration=1, velocity=64), scale_type)

    def get_chord_quality_for_degree(self, degree: int) -> ChordQualityType:
        # Return a chord quality based on the degree
        if degree < 1 or degree > 7:
            raise ValueError("Degree must be between 1 and 7")
        if degree == 1 or degree == 4:
            return ChordQualityType.MAJOR
        elif degree == 2 or degree == 3 or degree == 6:
            return ChordQualityType.MINOR
        elif degree == 5:
            return ChordQualityType.DOMINANT_7
        elif degree == 7:
            return ChordQualityType.DIMINISHED
        else:
            raise ValueError("Invalid degree")

class Chord(BaseModel):
    root: Note
    quality: ChordQualityType
    notes: List[Note] = Field(default_factory=list)
    inversion: int = 0

    def __init__(self, root: Note, quality: str, notes: Optional[List[Note]] = None, inversion: int = 0):
        if not isinstance(root, Note):
            raise ValueError("Root must be a valid Note instance.")
        try:
            self.quality = ChordQualityType(quality)
        except ValueError:
            raise ValueError(f'Invalid quality: {quality}')  # Handle invalid quality here
        super().__init__(root=root, quality=self.quality, notes=notes or [], inversion=inversion)