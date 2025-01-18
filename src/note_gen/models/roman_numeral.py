from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.scale import Scale

class RomanNumeral:
    ROMAN_TO_INT = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}
    INT_TO_ROMAN = {v: k for k, v in ROMAN_TO_INT.items()}

    def __init__(self, scale_degree: int = None, quality: ChordQualityType = None):
        self.scale_degree = scale_degree
        self.quality = quality if quality is not None else ChordQualityType.MAJOR

    @classmethod
    def from_scale_degree(cls, degree: int, quality: ChordQualityType) -> str:
        if degree not in cls.INT_TO_ROMAN:
            raise ValueError(f"Unsupported scale degree: {degree} (must be 1..7).")

        numeral = cls.INT_TO_ROMAN[degree]

        # Basic triads
        if quality == ChordQualityType.MINOR:
            return numeral.lower()
        elif quality == ChordQualityType.DIMINISHED:
            return numeral.lower() + 'o'
        elif quality == ChordQualityType.AUGMENTED:
            return numeral + '+'
        
        # 7th chords (example)
        elif quality == ChordQualityType.MINOR_7:
            return numeral.lower() + '7'
        elif quality == ChordQualityType.MAJOR_7:
            return numeral + 'Δ'  # Some people use "Δ7" for major7
        elif quality == ChordQualityType.DOMINANT:
            return numeral + '7'
        
        # Fallback: treat as major triad if none above
        return numeral

    @classmethod
    def from_string(cls, numeral: str) -> 'RomanNumeral':
        """Convert a Roman numeral string to a RomanNumeral instance."""
        if not isinstance(numeral, str):
            raise TypeError(f"Expected string, got {type(numeral)}")

        # Handle patterns with dashes (e.g. 'I-IV-V')
        if '-' in numeral:
            return [cls.from_string(n) for n in numeral.split('-')]

        # Check for quality modifiers
        quality = ChordQualityType.MAJOR  # Default quality
        base_numeral = numeral  # Keep original case for comparison

        # Handle diminished chords first
        if 'o' in numeral.lower():
            quality = ChordQualityType.DIMINISHED
            base_numeral = base_numeral.replace('O', '').replace('o', '')
        # Check if the numeral is lowercase (indicates minor)
        elif numeral.islower() and numeral.upper() in cls.ROMAN_TO_INT:
            quality = ChordQualityType.MINOR
            base_numeral = numeral.upper()
        elif '+' in numeral:
            quality = ChordQualityType.AUGMENTED
            base_numeral = base_numeral.replace('+', '')
        elif '7' in numeral:
            if numeral.islower():
                quality = ChordQualityType.MINOR_7
            else:
                quality = ChordQualityType.DOMINANT_7
            base_numeral = base_numeral.replace('7', '')
        else:
            base_numeral = numeral.upper()

        # Convert Roman numeral to scale degree
        try:
            scale_degree = cls.ROMAN_TO_INT[base_numeral]
            return cls(scale_degree=scale_degree, quality=quality)
        except KeyError:
            raise ValueError(f"Invalid Roman numeral: {numeral}")

    @classmethod
    def to_scale_degree(cls, numeral: str) -> int:
        """Convert a Roman numeral to its corresponding scale degree."""
        roman = cls.from_string(numeral)
        return roman.scale_degree

    @classmethod
    def get_roman_numeral_from_chord(cls, chord: Chord, scale: Scale) -> str:
        # Convert chord.root to a scale degree, or raise error if not found
        try:
            scale_degree = scale.get_degree_of_note(chord.root)
        except ValueError as e:
            raise ValueError(f"Failed to get degree of note {chord.root} in scale {scale}: {str(e)}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while getting degree of note {chord.root} in scale {scale}: {str(e)}")

        quality = chord.quality or ChordQualityType.MAJOR

        return cls.from_scale_degree(scale_degree, quality)