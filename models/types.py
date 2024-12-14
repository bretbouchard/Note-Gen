from enum import Enum, auto

class AccidentalType(Enum):
    """Represents musical accidentals."""
    NATURAL = auto()
    SHARP = auto()
    FLAT = auto()
    DOUBLE_SHARP = auto()
    DOUBLE_FLAT = auto()
