from enum import Enum
from pydantic import BaseModel, ConfigDict

class ChordQuality(str, Enum):
    """Enum representing the quality of a chord."""
    major = 'major'
    major_oct = 'major_oct'
    minor = 'minor'
    minor_oct = 'minor_oct'
    diminished = 'diminished'
    diminished_oct = 'diminished_oct'
    augmented = 'augmented'
    augmented_oct = 'augmented_oct'
    dominant7 = 'dominant7'
    dominant7_oct = 'dominant7_oct'
    major7 = 'major7'
    minor7 = 'minor7'
    diminished7 = 'diminished7'
    half_diminished7 = 'half_diminished7'
    augmented7 = 'augmented7'
    major9 = 'major9'
    minor9 = 'minor9'
    dominant9 = 'dominant9'
    major11 = 'major11'
    minor11 = 'minor11'
    sus2 = 'sus2'
    sus4 = 'sus4'
    seven_sus4 = '7sus4'

class ChordQualityModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
