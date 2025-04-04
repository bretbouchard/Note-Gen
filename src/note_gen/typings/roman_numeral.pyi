# roman_numeral.pyi

from typing import ClassVar, Optional, List

from src.note_gen.models.chord import Chord
from src.note_gen.models.scale_degree import ScaleDegree

class RomanNumeral:
    QUALITY_MODIFIERS: ClassVar[dict[str, tuple[str, List[int]]]]
    EXTENSIONS: ClassVar[dict[str, List[int]]]
    INVERSION_NOTATION: ClassVar[dict[int, str]]

    def __init__(self, numeral: str, scale_degree: ScaleDegree) -> None:
        ...
    def to_chord(self) -> Optional[Chord]:
        ...
