from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Chord
from src.note_gen.models.scale_degree import ScaleDegree
from src.note_gen.models.scale import Scale

class RomanNumeral:
    ROMAN_TO_INT = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}
    INT_TO_ROMAN = {v: k for k, v in ROMAN_TO_INT.items()}

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
    def to_scale_degree(cls, numeral: str) -> int:
        # Uppercase string to check in dictionary
        numeral_upper = numeral.upper()
        if numeral_upper not in cls.ROMAN_TO_INT:
            raise ValueError(f"Invalid roman numeral: {numeral}")
        return cls.ROMAN_TO_INT[numeral_upper]

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