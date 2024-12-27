"""Module for generating chord progressions."""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Tuple, ClassVar
from pydantic import BaseModel, Field
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.musical_elements import Note, Chord  # Update import statement
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.scale_info import ScaleInfo  # Update import statement

import logging
import random

logger = logging.getLogger(__name__)


class ProgressionPattern(str, Enum):
    """Common chord progression patterns."""

    BASIC_I_IV_V_I = "I-IV-V-I"
    POP_I_V_vi_IV = "I-V-vi-IV"
    BLUES_I_IV_I_V = "I-IV-I-V"
    JAZZ_ii_V_I = "ii-V-I"
    FIFTIES_I_vi_IV_V = "I-vi-IV-V"
    CANON_I_V_vi_iii_IV_I_IV_V = "I-V-vi-iii-IV-I-IV-V"
    MINOR_i_iv_v = "i-iv-v"
    MINOR_i_VI_III_VII = "i-VI-III-VII"


class ChordProgressionGenerator(BaseModel):
    """Generator for chord progressions."""

    def __init__(
        self,
        *,
        scale_info: ScaleInfo,
        progression_length: int = 4,
        pattern: Optional[ProgressionPattern] = None,
    ) -> None:
        super().__init__(
            scale_info=scale_info,
            progression_length=progression_length,
            pattern=pattern,
        )

    scale_info: ScaleInfo
    progression_length: int = Field(default=4, gt=0)  # Add gt=0 to the Field
    pattern: Optional[ProgressionPattern] = None

    # Define common chord qualities for major and minor scales
    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "major",  # I
        2: "minor",  # ii
        3: "minor",  # iii
        4: "major",  # IV
        5: "major",  # V
        6: "minor",  # vi
        7: "diminished",  # vii°
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "minor",  # i
        2: "diminished",  # ii°
        3: "major",  # III
        4: "minor",  # iv
        5: "minor",  # v
        6: "major",  # VI
        7: "major",  # VII
    }

    # Define common progression patterns
    PROGRESSION_PATTERNS: ClassVar[Dict[ProgressionPattern, List[Tuple[int, str]]]] = {
        ProgressionPattern.BASIC_I_IV_V_I: [
            (1, "major"),
            (4, "major"),
            (5, "major"),
            (1, "major"),
        ],
        ProgressionPattern.POP_I_V_vi_IV: [
            (1, "major"),
            (5, "major"),
            (6, "minor"),
            (4, "major"),
        ],
        ProgressionPattern.BLUES_I_IV_I_V: [
            (1, "major7"),
            (4, "major7"),
            (1, "major7"),
            (5, "dominant7"),
        ],
        ProgressionPattern.JAZZ_ii_V_I: [
            (2, "minor7"),
            (5, "dominant7"),
            (1, "major7"),
        ],
        ProgressionPattern.FIFTIES_I_vi_IV_V: [
            (1, "major"),
            (6, "minor"),
            (4, "major"),
            (5, "major"),
        ],
        ProgressionPattern.CANON_I_V_vi_iii_IV_I_IV_V: [
            (1, "major"),
            (5, "major"),
            (6, "minor"),
            (3, "minor"),
            (4, "major"),
            (1, "major"),
            (4, "major"),
            (5, "major"),
        ],
        ProgressionPattern.MINOR_i_iv_v: [(1, "minor"), (4, "minor"), (5, "minor")],
        ProgressionPattern.MINOR_i_VI_III_VII: [
            (1, "minor"),
            (6, "major"),
            (3, "major"),
            (7, "major"),
        ],
    }

    CHORD_INTERVALS: ClassVar[Dict[str, List[int]]] = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "diminished": [0, 3, 6],
        "major7": [0, 4, 7, 11],
        "minor7": [0, 3, 7, 10],
        "dominant7": [0, 4, 7, 10],
    }

    @classmethod
    def validate_scale_info(cls, v: ScaleInfo) -> ScaleInfo:
        if not isinstance(v, ScaleInfo):
            raise ValueError("scale_info must be an instance of ScaleInfo.")
        return v

    @classmethod
    def validate_progression_length(cls, v: int) -> int:
        if not isinstance(v, int) or v <= 0:
            raise ValueError("progression_length must be a positive integer.")
        return v

    @classmethod
    def validate_pattern(
        cls, v: Optional[ProgressionPattern]
    ) -> Optional[ProgressionPattern]:
        if v is not None and not isinstance(v, ProgressionPattern):
            raise ValueError(
                "pattern must be an instance of ProgressionPattern or None."
            )
        return v

    def get_chord_quality(self, scale_degree: int, is_minor: bool = False) -> str:
        """Get the default chord quality for a scale degree."""
        qualities = (
            self.MINOR_SCALE_QUALITIES if is_minor else self.MAJOR_SCALE_QUALITIES
        )
        return qualities[scale_degree]

    def _generate_chord_notes(self, root: Note, quality: str) -> List[Note]:
        intervals = self.CHORD_INTERVALS[quality]
        chord_notes = []
        for interval in intervals:
            note = root.transpose(interval)  # Assuming Note has a transpose method
            chord_notes.append(note)
        return chord_notes

    def generate(
        self, pattern: Optional[ProgressionPattern] = None, progression_length: int = 4
    ) -> ChordProgression:
        if not isinstance(pattern, ProgressionPattern) and pattern is not None:
            logger.error("Invalid progression pattern type, raising ValueError.")
            raise ValueError("Invalid progression pattern.")
        if pattern is None:
            logger.error("Pattern is None, raising ValueError.")
            raise ValueError("Invalid progression pattern.")
        logger.debug(f"Generating progression with pattern: {pattern}")
        logger.info("Generating chord progression with pattern: %s", pattern)
        chords = []

        if pattern not in self.PROGRESSION_PATTERNS:
            logger.error(f"Invalid pattern: {pattern}")
            raise ValueError(f"Invalid pattern: {pattern}")

        logger.debug(f"Pattern {pattern} is valid")
        scale_degrees = self.PROGRESSION_PATTERNS[pattern]

        # Ensure scale degrees are computed before accessing them
        self.scale_info.compute_scale_degrees()  # Assuming this method exists to compute scale degrees

        for degree, quality in scale_degrees:
            root_note = self.scale_info.get_scale_degree(degree)
            if not root_note:
                raise ValueError(f"Invalid scale degree: {degree}")

            # Create the chord based on the root note and quality
            chord = Chord(root=root_note, quality=ChordQualityType[quality.upper()])
            chords.append(chord)
            logger.debug("Generated chord: %s", chord)

        progression = ChordProgression(scale_info=self.scale_info, chords=chords)
        logger.info("Final chords generated: %d", len(chords))
        return progression

    def generate_custom(
        self, degrees: List[int], qualities: List[str]
    ) -> ChordProgression:
        """Generate a custom chord progression based on specified degrees and qualities."""
        try:
            logger.info(
                f"Generating custom progression with degrees: {degrees} and qualities: {qualities}"
            )
            if len(degrees) != len(qualities):
                logger.error("Degrees and qualities lists must be of the same length.")
                raise ValueError(
                    "Degrees and qualities lists must be of the same length."
                )

            chords = []
            for degree, quality in zip(degrees, qualities):
                logger.info(
                    f"Generating chord for degree: {degree}, quality: {quality}"
                )

                # More explicit root note handling
                root = None
                try:
                    if 0 <= degree - 1 < len(self.scale_info.scale_notes):
                        root = self.scale_info.scale_notes[degree - 1]
                except IndexError:
                    logger.error(f"Degree {degree} is out of range for scale notes")
                    continue

                if root is None or not isinstance(root, Note):
                    logger.error(f"Invalid root note for degree: {degree}")
                    continue

                chord_notes = self._generate_chord_notes(root, quality)
                if chord_notes is None or any(
                    note is None or not isinstance(note, Note) for note in chord_notes
                ):
                    logger.error(
                        f"Failed to generate valid chord notes for root: {root} and quality: {quality}"
                    )
                    continue

                logger.info(
                    f"Generating chord for degree: {degree}, quality: {quality}, root: {root}"
                )
                logger.info(
                    f"Creating Chord instance with degree: {degree}, quality: {quality}, root: {root}"
                )
                bass = Note.from_midi(
                    root.midi_number - 12
                )  # Transpose down by one octave for bass
                logger.info(f"Creating bass note for degree: {degree}, bass: {bass}")
                # Ensure chord_notes is populated correctly before creating the Chord instance
                if chord_notes is None or not all(isinstance(note, Note) for note in chord_notes):
                    logger.error(
                        f"Failed to generate valid chord notes for root: {root} and quality: {quality}"
                    )
                    continue
                chord = Chord(
                    root=root,
                    quality=ChordQualityType(quality),
                    notes=chord_notes,
                    # bass=bass,
                )
                chords.append(chord)
                logger.info(
                    f"Generated chord - Root: {root}, Bass: {bass}, Chord Notes: {chord_notes}"
                )
            progression = ChordProgression(scale_info=self.scale_info, chords=chords)
            return progression
        except Exception as e:
            logger.error(f"Failed to generate custom chord progression: {str(e)}")
            raise

    def generate_random(self, length: int) -> ChordProgression:
        """Generate a random chord progression of the specified length."""
        try:
            logger.info(f"Generating random progression of length: {length}")
            if length <= 0:
                logger.error("Length must be a positive integer.")
                raise ValueError("Length must be a positive integer.")

            chords = []
            for _ in range(length):
                degree = random.choice(list(self.MAJOR_SCALE_QUALITIES.keys()))
                quality = random.choice(list(self.MAJOR_SCALE_QUALITIES.values()))
                logger.info(
                    f"Generating chord for degree: {degree}, quality: {quality}"
                )

                try:
                    root = self.scale_info.scale_notes[
                        degree - 1
                    ]  # Adjust for 0-indexing
                except IndexError:
                    logger.error(f"Degree {degree} is out of range for scale notes")
                    continue

                chord_notes = self._generate_chord_notes(root, quality)
                if chord_notes is None or any(
                    note is None or not isinstance(note, Note) for note in chord_notes
                ):
                    logger.error(
                        f"Failed to generate valid chord notes for root: {root} and quality: {quality}"
                    )
                    continue

                logger.info(
                    f"Generating chord for degree: {degree}, quality: {quality}, root: {root}"
                )
                logger.info(
                    f"Creating Chord instance with degree: {degree}, quality: {quality}, root: {root}"
                )
                bass = Note.from_midi(
                    root.midi_number - 12
                )  # Transpose down by one octave for bass
                logger.info(f"Creating bass note for degree: {degree}, bass: {bass}")
                chord = Chord(
                    root=root,
                    quality=ChordQualityType(quality),
                    notes=chord_notes,
                    # bass=bass,
                )
                chords.append(chord)
                logger.info(
                    f"Generated chord - Root: {root}, Bass: {bass}, Chord Notes: {chord_notes}"
                )

            progression = ChordProgression(scale_info=self.scale_info, chords=chords)
            return progression
        except Exception as e:
            logger.error(f"Failed to generate random chord progression: {str(e)}")
            raise

    def get_chord_progression(self) -> List[Chord]:
        # Implementation here
        pass

    def generate_chord(self, numeral: str) -> Chord:
        """Generate a chord based on the given numeral."""
        # Determine the scale degree from the numeral
        scale_degree = self._parse_numeral(numeral)
        if scale_degree is None:
            raise ValueError(f"Invalid numeral: {numeral}")

        # Determine if the chord is minor
        is_minor = numeral.islower() or "m" in numeral

        # Get the chord quality
        quality = self.get_chord_quality(scale_degree, is_minor)

        # Get the root note from scale info
        root_note = self.scale_info.root

        # Generate chord notes
        chord_notes = self._generate_chord_notes(root_note, quality)

        # Validate chord notes
        if chord_notes is None or not all(
            isinstance(note, Note) for note in chord_notes
        ):
            logger.error(
                f"Failed to generate valid chord notes for root: {root_note} and quality: {quality}"
            )
            raise ValueError(
                f"Failed to generate valid chord notes for root: {root_note} and quality: {quality}"
            )

        logger.info(
            f"Generating chord for degree: {scale_degree}, quality: {quality}, root: {root_note}"
        )
        logger.info(
            f"Creating Chord instance with degree: {scale_degree}, quality: {quality}, root: {root_note}"
        )
        # Create and return the Chord object
        bass = Note.from_midi(
            root_note.midi_number - 12
        )  # Transpose down by one octave for bass
        logger.info(f"Creating bass note for degree: {scale_degree}, bass: {bass}")
        return Chord(
            root=root_note,
            quality=ChordQualityType(quality),
            notes=chord_notes,
            # bass=bass,
        )

    def _parse_numeral(self, numeral: str) -> Optional[int]:
        """Parse a Roman numeral to a scale degree."""
        if "/" in numeral:
            # Handle compound numerals (e.g., I/V)
            parts = numeral.split("/")
            return self._parse_numeral(parts[0])  # Return the first part for now

        numeral_map = {
            "I": 1,
            "ii": 2,
            "iii": 3,
            "IV": 4,
            "V": 5,
            "vi": 6,
            "vii": 7,
            "i": 1,
            "iv": 4,
            "v": 5,
            "VI": 6,
            "VII": 7,
            "bIII": 3,
            "bVI": 6,
            "bII": 2,
            "bVII": 7,
            "bI": 1,
            "III": 3,
        }
        return numeral_map.get(numeral)

    def get_scale(self) -> ScaleInfo:
        # Implementation here
        return self.scale_info
