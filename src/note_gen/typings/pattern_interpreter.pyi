# pattern_interpreter.pyi

from typing import List

from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.patterns import NotePattern
from src.note_gen.models.scale_info import ScaleInfo

class PatternInterpreter:
    def interpret(self, pattern: NotePattern, chord: Chord, scale_info: ScaleInfo) -> List[Note]: ...

class ArpeggioPatternInterpreter(PatternInterpreter):
    def interpret(self, pattern: NotePattern, chord: Chord, scale_info: ScaleInfo) -> List[Note]: ...

class ScalePatternInterpreter(PatternInterpreter):
    def interpret(self, pattern: NotePattern, chord: Chord, scale_info: ScaleInfo) -> List[Note]: ...
