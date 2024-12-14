# note_pattern.pyi

from typing import Union, List
from models.note import Note
from models.scale_degree import ScaleDegree
from models.chord import Chord

class NotePatternData:
    notes: List[Union[Note, ScaleDegree, Chord]]
    intervals: List[int] | None
    duration: float
    position: float
    velocity: int | None
    direction: str
    use_chord_tones: bool
    use_scale_mode: bool
    arpeggio_mode: bool
    restart_on_chord: bool
    octave_range: List[int] | None
    default_duration: float

class NotePattern:
    name: str
    data: NotePatternData
    description: str | None
    tags: List[str]
    complexity: float
    style: str | None
    default_duration: float