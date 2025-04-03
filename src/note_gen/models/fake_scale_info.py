"""Model for fake scale information used in tests."""
import re
from pydantic import BaseModel, Field, field_validator, ConfigDict
from note_gen.core.enums import ScaleType

class FakeScaleInfo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    key: str = Field(..., description="Scale key (e.g., 'C4' or 'F#4')")
    scale_type: ScaleType = Field(..., description="Scale type")
    complexity: float = Field(..., ge=0, le=1, description="Complexity (0-1)")

    @field_validator('key', mode='before')
    def validate_key(cls, v: str) -> str:
        v = v.strip()
        # Accept either full format with digit or if digit missing, default to 4.
        import re
        m = re.fullmatch(r'^([A-G][#b]?)(\d)?$', v)
        if m:
            note, octave = m.groups()
            return note + (octave if octave is not None else "4")
        raise ValueError(f"Invalid key format: {v}")

    @property
    def root(self) -> str:
        # Return just the note portion (e.g. "C4" becomes "C")
        import re
        m = re.fullmatch(r'^([A-G][#b]?)(\d)$', self.key)
        if m:
            return m.group(1)
        else:
            raise ValueError(f"Invalid key format: {self.key}")

    @property
    def type(self) -> ScaleType:
        return self.scale_type

    def get_note_display_name(self, note: str) -> str:
        note = note.strip()
        if re.fullmatch(r'^[A-G][#b]?\d$', note):
            return note
        else:
            raise ValueError(f"Invalid note format: {note}")

    def get_scale_notes(self) -> list:
        note_order = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        try:
            idx = note_order.index(self.root)
        except ValueError:
            raise ValueError(f"Invalid root note: {self.root}")
        if self.scale_type == ScaleType.MAJOR:
            intervals = [0, 2, 4, 5, 7, 9, 11]
        else:
            intervals = [0, 2, 3, 5, 7, 8, 10]
        return [note_order[(idx + interval) % 12] for interval in intervals]