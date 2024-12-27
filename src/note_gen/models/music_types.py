"""Module defining musical types, including accidentals."""

from enum import Enum, auto
from pydantic import BaseModel, Field, ConfigDict
from src.note_gen.models.enums import AccidentalType


class MusicTypes(BaseModel):
    accidental: AccidentalType = Field(..., description='Type of accidental')
    accidental_info: dict = Field({}, description='Additional information about the accidental')
    model_config = ConfigDict(arbitrary_types_allowed=True)
