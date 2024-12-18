# pattern_interpreter.pyi

from typing import List
from models.chord import Chord
from src.models.note import Note
from models.patterns import NotePattern
from models.scale_info import ScaleInfo

class PatternInterpreter:
    def interpret(self, pattern: NotePattern, chord: Chord, scale_info: ScaleInfo) -> List[Note]: ...

class ArpeggioPatternInterpreter(PatternInterpreter):
    def interpret(self, pattern: NotePattern, chord: Chord, scale_info: ScaleInfo) -> List[Note]: ...

class ScalePatternInterpreter(PatternInterpreter):
    def interpret(self, pattern: NotePattern, chord: Chord, scale_info: ScaleInfo) -> List[Note]: ...
