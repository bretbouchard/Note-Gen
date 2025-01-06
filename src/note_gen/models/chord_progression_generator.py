# src/note_gen/models/chord_progression_generator.py

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from typing import Optional, Dict, List, Tuple, ClassVar
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.chord_progression import ChordProgression

import logging
import random

logger = logging.getLogger(__name__)

class ChordProgressionGenerator(BaseModel):
    """Generator for chord progressions."""

    scale_info: ScaleInfo
    progression_length: int = Field(default=4, gt=0)
    pattern: Optional[List[str]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Define common chord qualities for major and minor scales
    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "major",      # I
        2: "minor",      # ii
        3: "minor",      # iii
        4: "major",      # IV
        5: "major",      # V
        6: "minor",      # vi
        7: "diminished", # vii°
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "minor",      # i
        2: "diminished", # ii°
        3: "major",      # III
        4: "minor",      # iv
        5: "minor",      # v
        6: "major",      # VI
        7: "major",      # VII
    }

    # Define common progression patterns
    PROGRESSION_PATTERNS: ClassVar[Dict[str, List[Tuple[int, str]]]] = {
        "I-IV-V": [
            (1, "major"),
            (4, "major"),
            (5, "major"),
        ],
        "I-V-vi-IV": [
            (1, "major"),
            (5, "major"),
            (6, "minor"),
            (4, "major"),
        ],
        # Add more patterns as needed
    }

    CHORD_INTERVALS: ClassVar[Dict[str, List[int]]] = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "diminished": [0, 3, 6],
        "augmented": [0, 4, 8],
        "major7": [0, 4, 7, 11],
        "minor7": [0, 3, 7, 10],
        "dominant7": [0, 4, 7, 10],
    }

    def get_chord_quality(self, scale_degree: int, is_minor: bool = False) -> str:
        """Get the default chord quality for a scale degree."""
        qualities = (
            self.MINOR_SCALE_QUALITIES if is_minor else self.MAJOR_SCALE_QUALITIES
        )
        return qualities.get(scale_degree, "major")

    def _generate_chord_notes(self, root: Note, quality: str) -> List[Note]:
        """Generate chord notes based on root and quality."""
        intervals = self.CHORD_INTERVALS.get(quality)
        if not intervals:
            logger.error(f"Unknown chord quality: {quality}")
            raise ValueError(f"Unknown chord quality: {quality}")
        chord_notes = []
        for interval in intervals:
            try:
                note = root.transpose(interval)
                chord_notes.append(note)
            except ValueError as e:
                logger.error(f"Error transposing note: {e}")
                raise
        return chord_notes

    def generate(
        self, pattern: Optional[List[str]] = None, progression_length: int = 4
    ) -> ChordProgression:
        if pattern is None:
            if self.pattern is None:
                raise ValueError("No progression pattern provided.")
            pattern = self.pattern

        if not all(p in self.PROGRESSION_PATTERNS for p in pattern):
            logger.error(f"Invalid pattern: {pattern}")
            raise ValidationError(f"Invalid pattern: {pattern}")

        logger.debug(f"Generating progression with pattern: {pattern}")
        chords = []
        for p in pattern:
            scale_degrees = self.PROGRESSION_PATTERNS[p]
            for degree, quality in scale_degrees:
                logger.debug(f"Generating chord for degree: {degree}, quality: {quality}")
                chord_quality = quality
                root_note = self.scale_info.get_scale_degree_note(degree)
                if not root_note:
                    logger.error(f"Invalid scale degree: {degree}")
                    raise ValueError(f"Invalid scale degree: {degree}")

                # Handle extended qualities like major7, minor7, dominant7
                quality_enum = ChordQualityType[quality.upper()]

                # Create the chord
                chord = Chord(root=root_note, quality=quality_enum)
                chords.append(chord)
                logger.debug(f"Generated chord: {chord}")

        progression = ChordProgression(scale_info=self.scale_info, chords=chords)
        logger.info(f"Final chords generated: {len(chords)}")
        return progression

    def generate_custom(
        self, degrees: List[int], qualities: List[str]
    ) -> ChordProgression:
        """Generate a custom chord progression based on specified degrees and qualities."""
        if len(degrees) != len(qualities):
            logger.error("Degrees and qualities lists must be of the same length.")
            raise ValueError("Degrees and qualities lists must be of the same length.")

        chords = []
        for degree, quality in zip(degrees, qualities):
            logger.debug(f"Generating chord for degree: {degree}, quality: {quality}")
            chord_quality = quality
            root_note = self.scale_info.get_scale_degree_note(degree)
            if not root_note:
                logger.error(f"Invalid scale degree: {degree}")
                raise ValueError(f"Invalid scale degree: {degree}")

            # Handle extended qualities like major7, minor7, dominant7
            quality_enum = ChordQualityType.get(quality.upper())
            if not quality_enum:
                logger.error(f"Unknown chord quality: {quality}")
                raise ValueError(f"Unknown chord quality: {quality}")

            # Create the chord
            chord = Chord(root=root_note, quality=quality_enum)
            chords.append(chord)
            logger.debug(f"Generated chord: {chord}")

        progression = ChordProgression(scale_info=self.scale_info, chords=chords)
        logger.info(f"Final chords generated: {len(chords)}")
        return progression

    def generate_random(self, length: int) -> ChordProgression:
        """Generate a random chord progression of the specified length."""
        if length <= 0:
            logger.error("Length must be a positive integer.")
            raise ValueError("Length must be a positive integer.")

        chords = []
        for _ in range(length):
            degree = random.choice(list(self.MAJOR_SCALE_QUALITIES.keys()))
            quality = random.choice(list(self.MAJOR_SCALE_QUALITIES.values()))
            logger.debug(f"Generating random chord for degree: {degree}, quality: {quality}")

            root_note = self.scale_info.get_scale_degree_note(degree)
            if not root_note:
                logger.error(f"Invalid scale degree: {degree}")
                raise ValueError(f"Invalid scale degree: {degree}")

            quality_enum = ChordQualityType[quality.upper()]

            # Create the chord
            chord = Chord(root=root_note, quality=quality_enum)
            chords.append(chord)
            logger.debug(f"Generated chord: {chord}")

        progression = ChordProgression(scale_info=self.scale_info, chords=chords)
        logger.info(f"Final chords generated: {len(chords)}")
        return progression

    def generate_chord(self, numeral: str) -> Chord:
        """Generate a chord based on the given numeral."""
        logger.info("Generating chord for numeral: %s", numeral)
        degree = self._parse_numeral(numeral)

        if not degree:
            logger.error(f"Invalid numeral: {numeral}")
            raise ValueError(f"Invalid numeral: {numeral}")

        quality = self.scale_info.get_chord_quality_for_degree(degree)
        if not quality:
            logger.error(f"Cannot determine chord quality for degree: {degree}")
            raise ValueError(f"Cannot determine chord quality for degree: {degree}")

        root_note = self.scale_info.get_scale_degree_note(degree)
        if not root_note:
            logger.error(f"No root note found for degree: {degree}")
            raise ValueError(f"No root note found for degree: {degree}")

        # Handle extended qualities like major7, minor7, dominant7
        try:
            quality_enum = ChordQualityType[quality.upper()]
        except KeyError:
            logger.error(f"Unknown chord quality: {quality}")
            raise ValueError(f"Unknown chord quality: {quality}")

        chord = Chord(root=root_note, quality=quality_enum)
        logger.debug("Generated chord: %s", chord)
        return chord

    def _parse_numeral(self, numeral: str) -> Optional[int]:
        """Parse a Roman numeral to a scale degree."""
        import re  # Local import to prevent circular dependency

        # Remove any modifiers like 'o', '+', '7', etc.
        base_numeral = re.match(r'^[IVX]+', numeral.upper())
        if not base_numeral:
            return None
        base_numeral = base_numeral.group()

        numeral_map = {
            "I": 1,
            "II": 2,
            "III": 3,
            "IV": 4,
            "V": 5,
            "VI": 6,
            "VII": 7,
        }
        return numeral_map.get(base_numeral)