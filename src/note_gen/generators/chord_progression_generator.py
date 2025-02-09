from __future__ import annotations
from typing import List, Dict, ClassVar, Optional, Tuple, Union
import random
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from pydantic import BaseModel, ValidationError, Field

from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.fake_scale_info import FakeScaleInfo

class ProgressionGenerator(BaseModel):
    """Base class for chord progressions."""
    
    name: str
    chords: List[Chord]
    key: str
    scale_type: str
    scale_info: FakeScaleInfo
    
    def generate_chord_progression_example(self) -> None:
        """Example method with proper return type and annotations."""
        pass

class ChordProgressionGenerator(BaseModel):
    """Generator for creating chord progressions."""

    name: str
    chords: List[Chord]
    key: str
    scale_type: str
    scale_info: Union[ScaleInfo, FakeScaleInfo] = Field(...)

    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)
    
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
    
    def __init__(self, name: str, chords: List[Chord], key: str, scale_type: str, scale_info: Union[ScaleInfo, FakeScaleInfo]):
        super().__init__(name=name, chords=chords, key=key, scale_type=scale_type, scale_info=scale_info)
        self.validate_inputs()

    def validate_inputs(self):
        if not self.chords:
            raise ValueError("Chords list cannot be empty.")
        if not isinstance(self.scale_info, (ScaleInfo, FakeScaleInfo)):
            raise ValueError("Invalid scale_info. Must be an instance of ScaleInfo or FakeScaleInfo.")

    def generate(self, pattern: Optional[List[str]] = None, progression_length: Optional[int] = None) -> ChordProgression:
        """
        Generate a chord progression based on either a pattern or a specified length.
        If both pattern and progression_length are provided, pattern takes precedence.
        
        Args:
            pattern: Optional list of Roman numeral patterns (e.g., ["I", "IV", "V"])
            progression_length: Optional length for random progression generation
            
        Raises:
            ValueError: If neither pattern nor progression_length is provided,
                      if pattern is empty, or if progression_length is not positive
        """
        if pattern is None and progression_length is None:
            raise ValueError("Must provide either a pattern or a progression_length")

        # Always validate progression_length if it's provided
        if progression_length is not None:
            if progression_length == 0:
                raise ValueError("progression_length cannot be 0")
            if progression_length < 0:
                raise ValueError("progression_length must be positive")

        if pattern is not None:
            # Handle empty pattern case
            if not pattern:
                raise ValueError("Pattern list cannot be empty")
                
            # If pattern is provided, use it to generate the progression
            expanded_pattern = self.expand_pattern(pattern)
            return self.generate_from_pattern(expanded_pattern)
        else:
            # If only progression_length is provided, generate random progression
            if progression_length is None:
                raise ValueError("progression_length must be provided when pattern is None")
            return self.generate_random(progression_length)

    def generate_random(self, length: int) -> ChordProgression:
        """Generate a random chord progression of specified length."""
        if length <= 0:
            raise ValueError("Length must be greater than 0")
            
        # Generate a random sequence of scale degrees
        degrees = [random.randint(1, 7) for _ in range(length)]
        
        # Get the corresponding chord qualities based on scale type
        qualities = []
        for degree in degrees:
            if self.scale_info.scale_type == "MAJOR":
                qualities.append(self.scale_info.MAJOR_SCALE_QUALITIES.get(degree, ChordQualityType.MAJOR))
            else:
                qualities.append(self.scale_info.MINOR_SCALE_QUALITIES.get(degree, ChordQualityType.MINOR))
        
        # Create the pattern from degrees and qualities
        pattern = list(zip(degrees, qualities))
        
        return self.generate_from_pattern(pattern)

    def convert_roman_to_chord(self, numeral: str) -> Chord:
        roman = RomanNumeral.from_string(numeral)  # Convert numeral to scale degree
        root = self.scale_info.root  # Get root note
        quality = self.scale_info.get_chord_quality_for_degree(roman.scale_degree)  # Get quality from scale
        quality = ChordQualityType.from_string(quality)  # Ensure quality is converted correctly
        return Chord(root=root, quality=quality)  # Create Chord instance

    def generate_from_pattern(self, pattern: List[Tuple[int, ChordQualityType]]) -> ChordProgression:
        """Generate a chord progression from a pattern of scale degrees and qualities."""
        chords = []
        for degree, quality in pattern:
            self.logger.debug(f"Generating chord for degree: {degree}, quality: {quality}")
            root = self.scale_info.get_note_for_degree(degree)
            if root is None:
                raise ValueError(f"Invalid degree: {degree}")
            
            # Create the chord with the root and quality
            chord = Chord(root=root, quality=quality)
            
            # Generate the notes for the chord
            chord.notes = chord._generate_chord_notes()
            
            chords.append(chord)
            
        # Log the values being passed to ChordProgression
        self.logger.debug(f"Creating ChordProgression with name: 'Generated Progression', chords: {chords}, key: {self.scale_info.root.note_name}, scale_type: {self.scale_info.scale_type}")
        return ChordProgression(
            name="Generated Progression",
            chords=chords,
            key=self.scale_info.root.note_name,
            scale_type=self.scale_info.scale_type,
            scale_info=self.scale_info
        )

    def generate_chord(self, root: Note, quality: Union[str, ChordQualityType]) -> Chord:
        if not isinstance(quality, ChordQualityType):
            quality = ChordQualityType.from_string(quality)  # Convert to ChordQualityType if necessary
        intervals = ChordQualityType.get_intervals(quality)
        try:
            chord = Chord(root=root, quality=quality)
        except ValidationError as e:
            self.logger.error(f"Error creating Chord instance: {e}")
            raise ValueError(f"Invalid root or quality for chord: {root}, {quality}") from e
        chord_notes = chord.generate_notes()  # Generate notes for the chord
        self.logger.debug(f"Generated chord notes: {chord_notes}")
        return chord
        
    def generate_chord_numeral(self, numeral: str) -> Chord:
        """Generate a chord based on the numeral provided."""
        self.logger.debug(f'Generating chord for numeral: {numeral}')  # Log the numeral being processed
        if numeral not in self.INT_TO_ROMAN.values():
            raise ValueError(f"Invalid numeral: {numeral}. Must be one of {list(self.INT_TO_ROMAN.values())}")
        roman = RomanNumeral.from_string(numeral)
        self.logger.debug(f'Converted numeral to Roman numeral: {roman}')  # Log the converted Roman numeral
        root = self.scale_info.root
        quality = self.scale_info.get_chord_quality_for_degree(roman.scale_degree)
        quality = ChordQualityType.from_string(quality)  # Ensure quality is converted correctly
        self.logger.debug(f'Root note: {root}, Quality: {quality}')  # Log root note and quality
        return Chord(root=root, quality=quality)

    def generate_chord_notes(self, root: Note, quality: Union[str, ChordQualityType], inversion: int = 0) -> List[Note]:
        """Generate the notes for a chord based on root, quality, and inversion."""
        # Validate that the quality is a valid member of ChordQualityType
        if not isinstance(quality, ChordQualityType):
            quality = ChordQualityType.from_string(quality)  # Convert to ChordQualityType if necessary
        intervals = ChordQualityType.get_intervals(quality)  # Pass the quality argument correctly
        try:
            chord = Chord(root=root, quality=quality)
        except ValidationError as e:
            self.logger.error(f"Error creating Chord instance: {e}")
            raise ValueError(f"Invalid root or quality for chord: {root}, {quality}") from e
        chord_notes = chord.generate_notes()  # Generate notes for the chord
        self.logger.debug(f"Generated chord notes: {chord_notes}")
        return chord_notes

    def expand_pattern(self, pattern: List[str]) -> List[Tuple[int, ChordQualityType]]:
        # This method expands a pattern of Roman numerals into a list of degrees and qualities.
        roman_to_degree = {
            'I': 1,
            'II': 2,
            'III': 3,
            'IV': 4,
            'V': 5,
            'VI': 6,
            'VII': 7,
            # Add lowercase variants
            'i': 1,
            'ii': 2,
            'iii': 3,
            'iv': 4,
            'v': 5,
            'vi': 6,
            'vii': 7,
        }
        qualities = {
            'maj': ChordQualityType.MAJOR,
            'min': ChordQualityType.MINOR,
            'dim': ChordQualityType.DIMINISHED,
            'aug': ChordQualityType.AUGMENTED,
            # Add more quality mappings
            'M': ChordQualityType.MAJOR,
            'm': ChordQualityType.MINOR,
            'o': ChordQualityType.DIMINISHED,
            '+': ChordQualityType.AUGMENTED,
            '°': ChordQualityType.DIMINISHED,
        }
        expanded = []
        for numeral in pattern:
            parts = numeral.split('-')  # Split by dash to handle multiple chords
            for part in parts:
                part = part.strip()
                # Extract quality from the numeral if it exists
                quality = ChordQualityType.MAJOR  # Default quality
                if part.islower():  # If the numeral is lowercase, it's minor by default
                    quality = ChordQualityType.MINOR
                
                # Check for explicit quality markers
                for q_suffix, q_type in qualities.items():
                    if part.endswith(q_suffix):
                        quality = q_type
                        part = part[:-len(q_suffix)]  # Remove quality suffix
                        break
                
                # Look up the degree
                degree = roman_to_degree.get(part)
                if degree is None:
                    raise ValueError(f"Unsupported Roman numeral: {part}")
                
                expanded.append((degree, quality))
        return expanded

    def generate_custom(self, degrees: List[int], qualities: List[Union[str, ChordQualityType]]) -> ChordProgression:
        logger.debug("generate_custom method called")
        logger.debug(f"Degrees: {degrees}, Qualities: {qualities}")
    
        if len(degrees) != len(qualities):
            raise ValueError("Degrees and qualities must have the same length.")
    
        chords = []
        for degree, quality in zip(degrees, qualities):
            logger.debug(f"Processing degree: {degree}, quality: {quality}")
            root = self.scale_info.get_note_for_degree(degree)
            if root is None:
                raise ValueError(f"Invalid degree: {degree}")
            logger.debug(f"Root Note is valid: {root}")
    
            if quality is None:
                quality = ChordQualityType.MAJOR  # Default to major if not provided
            if not isinstance(quality, ChordQualityType):
                quality = ChordQualityType.from_string(quality)  # Convert to ChordQualityType if necessary
            logger.debug(f"Chord Quality is valid: {quality}")
    
            # Create Chord instance and generate notes
            chord = Chord(root=root, quality=quality)
            logger.debug(f"Created Chord: root={chord.root}, quality={chord.quality}, notes={chord.notes}")

            chord.notes = chord.generate_notes()  # Populate the notes for the chord
            logger.debug(f"Creating Chord: root={root.note_name}, quality={quality}, notes={chord.notes}")
            chords.append(chord)
    
        # Validate ChordProgression fields
        progression = ChordProgression(
            name=self.name,
            chords=chords,
            key=self.key,
            scale_type=self.scale_type,
            scale_info=self.scale_info
        )
        return progression

    def generate_large(self, length: int) -> ChordProgression:
        if length <= 0:
            raise ValueError("Length must be greater than 0.")
        chords = [Chord(root=chord.root, quality=chord.quality) for chord in random.choices(self.chords, k=length)]  # Ensure quality is assigned
        return ChordProgression(
            name="Generated Progression",
            chords=chords,
            key=self.scale_info.root.note_name,
            scale_type=self.scale_info.scale_type,
            scale_info=self.scale_info,
            quality=chords[0].quality  # Set quality from the first chord
        )

class Scale(BaseModel):
    root: Note = Field(...)
    scale_type: str = Field(...)
    intervals: List[int] = Field(default_factory=list)

    def __init__(self, root: Note, scale_type: str) -> None:
        super().__init__(root=root, scale_type=scale_type)
        if not isinstance(scale_type, str):
            raise ValueError(f"Invalid scale type: {scale_type}")
        self.intervals = self.calculate_intervals()  # Ensure intervals are calculated on initialization