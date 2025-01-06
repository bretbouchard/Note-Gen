from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.musical_elements import Chord

class RomanNumeral:
    ROMAN_TO_INT = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}
    INT_TO_ROMAN = {v: k for k, v in ROMAN_TO_INT.items()}

    @classmethod
    def from_scale_degree(cls, degree: int, quality: ChordQualityType) -> str:
        numeral = cls.INT_TO_ROMAN[degree]
        if quality == ChordQualityType.MINOR:
            return numeral.lower()
        elif quality == ChordQualityType.DIMINISHED:
            return numeral.lower() + 'o'
        elif quality == ChordQualityType.AUGMENTED:
            return numeral + '+'
        return numeral

    @classmethod
    def to_scale_degree(cls, numeral: str) -> int:
        return cls.ROMAN_TO_INT[numeral.upper()]

    @classmethod
    def get_roman_numeral_from_chord(cls, chord: Chord) -> str:
        scale_degree = chord.root.octave  # Placeholder for actual scale degree logic
        quality = chord.quality
        return cls.from_scale_degree(scale_degree, quality)