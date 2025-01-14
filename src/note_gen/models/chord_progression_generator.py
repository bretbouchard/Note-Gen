from __future__ import annotations
from typing import List, Dict, ClassVar, Optional
import random
import logging
from pydantic import BaseModel, Field, ValidationError

from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.musical_elements import Chord, Note
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord_quality import ChordQuality, ChordQualityType
from src.note_gen.models.roman_numeral import RomanNumeral

logger = logging.getLogger(__name__)

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
        root = self.scale_info.get_note_for_degree(roman.scale_degree)  # Get root note
        quality = self.scale_info.get_chord_quality_for_degree(roman.scale_degree)  # Get quality from scale
        return Chord(root=root, quality=quality)  # Create Chord instance

    def generate_from_pattern(self, pattern: List[str]) -> ChordProgression:
        """Generate a chord progression from a pattern of Roman numerals."""
        chords = []
        for numeral in pattern:
            try:
                roman = RomanNumeral.from_string(numeral)  # Create RomanNumeral instance
                root = self.scale_info.get_scale_note_at_degree(roman.scale_degree)  # Get scale degree as integer
                chord = self.generate_chord(numeral)
                chords.append(chord)  # Append the Chord instance directly
            except (ValueError, ValidationError) as e:
                raise ValueError(f"Invalid Roman numeral in pattern: {numeral}") from e

        return ChordProgression(name="Generated Progression", scale_info=self.scale_info, chords=chords, key=self.scale_info.key)
    
    def generate_chord(self, roman_numeral: str) -> Chord:
        """Generate a chord from a Roman numeral."""
        try:
            roman = RomanNumeral.from_string(roman_numeral)
            root = self.scale_info.get_scale_note_at_degree(roman.scale_degree)
            # Get quality from scale_info
            quality = self.scale_info.get_chord_quality_for_degree(roman.scale_degree)
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
            
        return ChordProgression(name="Custom Progression", scale_info=self.scale_info, chords=chords, key=self.scale_info.key)