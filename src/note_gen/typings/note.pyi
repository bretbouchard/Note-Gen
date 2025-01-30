from typing import ClassVar, Optional, Union, List
from src.note_gen.models.scale_degree import ScaleDegree

class Note:
    NOTE_TO_NUMBER: ClassVar[dict[str, int]] = ...

    note_name: str
    accidental: str = ''
    octave: int = 4
    duration: float = 1.0
    midi_number: int
    position: Optional[float] = None
    pitch: Optional[str] = None
    midi_to_note: Optional[str] = None  # Converts MIDI number to note name
    to_note: Optional[str] = None  # Similar to midi_to_note
    degree: Optional[int] = None  # Scale degree (1 for tonic, etc.)
    key: Optional[str] = "C"  # Key of the scale
    scale_type: Optional[str] = "MAJOR"  # Type of scale (e.g., MAJOR, MINOR)
    octave_offset: int = 0  # Offset from middle C


    def __init__(self, pitch: str, duration: float) -> None:
        ...

    @classmethod
    def from_midi(cls, note_name: str, midi_number: int, duration: float = 1.0) -> 'Note':
        ...

    @classmethod
    def from_str(cls, note_name: str, note_str: str, duration: float = 1.0, default_octave: int = 4) -> 'Note':
        ...

    def get_enharmonic_equivalents(self) -> List['ScaleDegree']:
        ...

    def is_enharmonic(self, other: 'Note') -> bool:
        ...

    def interval(self, other: 'Note') -> int:
        ...

    # Comparison and arithmetic methods
    def __lt__(self, other: Union['Note', int]) -> bool:
        ...

    def __le__(self, other: Union['Note', int]) -> bool:
        ...

    def __gt__(self, other: Union['Note', int]) -> bool:
        ...

    def __ge__(self, other: Union['Note', int]) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        ...

    def __add__(self, other: Union['Note', int]) -> 'Note':
        ...

    def __sub__(self, other: Union['Note', int]) -> 'Note':
        ...

    def __radd__(self, other: int) -> 'Note':
        ...
