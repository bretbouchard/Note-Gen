# note_pattern.pyi

from typing import Union, List
from src.note_gen.models.note import Note
from src.note_gen.models.scale_degree import ScaleDegree

from src.note_gen.models.chord import Chord


class NotePatternData:
    notes: List[Union[Note, ScaleDegree, Chord]]
    intervals: List[int] | None
    duration: float
    position: float
    velocity: int
    direction: str
    use_chord_tones: bool
    use_scale_mode: bool
    arpeggio_mode: bool
    restart_on_chord: bool
    octave_range: List[int] | None
    default_duration: float
    index: int

class NotePattern:
    name: str
    id: str
    index: int
    data: NotePatternData
    description: str | None
    tags: List[str]
    complexity: float
    style: str | None
    default_duration: float