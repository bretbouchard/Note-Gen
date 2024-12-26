"""Module defining musical types, including accidentals."""

from enum import Enum, auto
from pydantic import BaseModel, Field, ConfigDict


class AccidentalType(Enum):
    """Represents musical accidentals.

    This enum defines the types of accidentals that can modify a note's pitch.
    Each accidental alters the note in a specific way:
    - NATURAL: Cancels any previous sharps or flats.
    - SHARP: Raises the pitch of a note by a semitone.
    - FLAT: Lowers the pitch of a note by a semitone.
    - DOUBLE_SHARP: Raises the pitch of a note by two semitones.
    - DOUBLE_FLAT: Lowers the pitch of a note by two semitones.
    """

    NATURAL = auto()
    SHARP = auto()
    FLAT = auto()
    DOUBLE_SHARP = auto()
    DOUBLE_FLAT = auto()


class MusicTypes(BaseModel):
    accidental: AccidentalType = Field(..., description='Type of accidental')
    accidental_info: dict = Field({}, description='Additional information about the accidental')
    model_config = ConfigDict(arbitrary_types_allowed=True)
