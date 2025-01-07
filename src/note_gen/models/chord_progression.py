# src/note_gen/models/chord_progression.py

from typing import List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.roman_numeral import RomanNumeral
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.scale import Scale, ScaleType
import logging

logger = logging.getLogger(__name__)

class ChordProgression(BaseModel):
    """Class representing a progression of chords."""

    scale_info: ScaleInfo
    chords: List[Chord] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("chords", mode="before")
    def validate_chords(cls, v: list[Any]) -> list[Chord]:
        if not v:
            raise ValueError("Chords cannot be empty.")
        for item in v:
            if not isinstance(item, Chord):
                raise ValueError("All items in chords must be instances of Chord.")
        return v

    def add_chord(self, chord: Chord) -> None:
        """Add a chord to the progression."""
        self.chords.append(chord)

    def get_chord_at(self, index: int) -> Chord:
        return self.chords[index]

    def get_all_chords(self) -> List[Chord]:
        return self.chords

    def get_chord_names(self) -> List[str]:
        scale = Scale(self.scale_info.root, self.scale_info.scale_type)
        return [
            RomanNumeral.get_roman_numeral_from_chord(chord, scale)
            for chord in self.chords
        ]

    def transpose(self, interval: int) -> None:
        logger.debug(f"Transposing progression by {interval} semitones")
        for chord in self.chords:
            if chord.root:
                logger.debug(f"Chord before transposition: root={chord.root.note_name}, quality={chord.quality}, notes={chord.notes}")
                new_midi_number = chord.root.midi_number + interval
                try:
                    new_root = Note.from_midi(midi_number=new_midi_number)
                except ValueError as e:
                    logger.error(f"Error transposing note: {e}")
                    raise ValueError(f"Error transposing note: {e}")
                
                new_quality = (
                    chord.quality or ChordQualityType.MAJOR
                )  # Default to MAJOR if None
                logger.debug(f"New root after transposition: {new_root.note_name}, new quality: {new_quality}")
                chord.root = new_root
                chord.quality = new_quality
                chord.notes = self.generate_chord_notes(new_root, new_quality, chord.inversion)
                logger.debug(f"Chord after transposition: root={chord.root.note_name}, quality={chord.quality}, notes={chord.notes}")
                logger.debug(
                    f"Transposed chord: root={new_root.note_name}, quality={new_quality}"
                )

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        d = super().dict(*args, **kwargs)
        d["chords"] = [chord.dict() for chord in self.chords]
        d["scale_info"] = self.scale_info.dict()
        return d

    def generate_chord_notes(self, root: Note, quality: ChordQualityType, inversion: int) -> List[Note]:
        """Generate chord notes based on root, quality, and inversion."""
        intervals_map = {
            ChordQualityType.MAJOR: [0, 4, 7],
            ChordQualityType.MINOR: [0, 3, 7],
            ChordQualityType.DIMINISHED: [0, 3, 6],
            ChordQualityType.AUGMENTED: [0, 4, 8],
        }

        intervals = intervals_map.get(quality, [0, 4, 7])
        chord_notes = [root.transpose(interval) for interval in intervals]
        # Handle inversion if needed
        if inversion:
            chord_notes = chord_notes[inversion:] + chord_notes[:inversion]
        return chord_notes