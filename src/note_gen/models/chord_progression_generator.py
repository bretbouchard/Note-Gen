# src/note_gen/models/chord_progression_generator.py

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from typing import Optional, Dict, List, Tuple, ClassVar
from src.note_gen.models.musical_elements import Note, Chord
from src.note_gen.models.scale_info import ScaleInfo
from src.note_gen.models.enums import ChordQualityType
from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.roman_numeral import RomanNumeral

import logging
import sys
import random
from typing import cast

# Change logger to print to stdout for test visibility
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)  # Set up logging to print to stdout

logger = logging.getLogger(__name__)  # Keep the logger configuration

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

    def generate(self, pattern: Optional[List[str]] = None, progression_length: int = 4) -> ChordProgression:
        # Validate the progression length
        if progression_length <= 0:
            logger.error("Progression length must be a positive integer.")
            raise ValueError("Progression length must be a positive integer.")

        # Validate the provided pattern against known patterns
        if pattern is None:
            pattern = self.pattern

        if pattern is None or len(pattern) == 0:
            logger.error("No progression pattern provided or provided pattern is empty.")
            raise ValueError("No progression pattern provided or provided pattern cannot be empty.")

        for p in pattern:
            if p not in self.PROGRESSION_PATTERNS:
                logger.error(f"Invalid progression pattern: {p}")
                raise ValueError(f"Invalid progression pattern: {p}")

        chords: List[Chord] = []  # Specify the type for chords
        logger.debug(f"Generating chords for pattern: {pattern}")

        # Calculate how many full patterns we can use
        full_patterns = progression_length // len(pattern)
        remaining_chords = progression_length % len(pattern)

        logger.debug(f"Full patterns: {full_patterns}, Remaining chords: {remaining_chords}")  # Log the number of full patterns and remaining chords

        # Generate chords for the full patterns
        for _ in range(full_patterns):
            for p in pattern:
                logger.debug(f"Processing pattern: {p}")  # Log the current pattern being processed
                pattern_degrees = self.PROGRESSION_PATTERNS[p]
                for degree, quality in pattern_degrees:
                    if len(chords) >= progression_length:
                        break
                    logger.debug(f"Generating chord for degree: {degree}, quality: {quality}")
                    root_note = self.scale_info.get_scale_degree_note(degree)
                    logger.debug(f"Root note for degree {degree}: {root_note.note_name if root_note else 'None'}")  # Log the root note

                    if not root_note:
                        logger.error(f"Invalid scale degree: {degree}")
                        raise ValueError(f"Invalid scale degree: {degree}")

                    logger.debug(f"Validating chord quality: {quality}")
                    if quality not in [q.value for q in ChordQualityType]:
                        logger.error(f"Unsupported chord type: {quality}")
                        raise ValueError(f"Unsupported chord type: {quality}")
                    quality_enum = ChordQualityType(quality)
                    logger.debug(f"Chord quality validated: {quality_enum}")

                    # Create the chord
                    chord_notes = self._generate_chord_notes(root_note, quality)
                    logger.debug(f"Generated chord notes for degree {degree}: {chord_notes}")  # Log the generated chord notes
                    chords.append(Chord(root=root_note, quality=quality_enum, notes=chord_notes))
                    logger.debug(f"Chord added: {chords[-1]}")

        logger.info(f"Final chords generated: {len(chords)}")
        logger.debug(f"Generated chords: {[str(chord) for chord in chords]}")  # Log the generated chords before returning
        return ChordProgression(scale_info=self.scale_info, chords=chords)

    def generate_custom(
        self, degrees: List[int], qualities: List[str]
    ) -> ChordProgression:
        """Generate a custom chord progression based on specified degrees and qualities."""
        if len(degrees) != len(qualities):
            logger.error("Degrees and qualities lists must be of the same length.")
            raise ValueError("Degrees and qualities lists must be of the same length.")

        chords: List[Chord] = []
        logger.debug(f"Generating custom chord progression for degrees: {degrees}, qualities: {qualities}")  # Log the custom progression details
        for degree, quality in zip(degrees, qualities):
            logger.debug(f"Generating chord for degree: {degree}, quality: {quality}")
            logger.debug(f"Quality before validation: {quality}")  # Log the quality before validation
            root_note = self.scale_info.get_scale_degree_note(degree)
            if not root_note:
                logger.error(f"Invalid scale degree: {degree}")
                raise ValueError(f"Invalid scale degree: {degree}")

            logger.debug(f"Validating chord quality: {quality}")
            if quality not in [q.value for q in ChordQualityType]:
                logger.error(f"Unsupported chord type: {quality}")
                raise ValueError(f"Unsupported chord type: {quality}")
            quality_enum = ChordQualityType(quality)
            logger.debug(f"Chord quality validated: {quality_enum}")
            # Create the chord
            chord_notes = self._generate_chord_notes(root_note, quality)
            logger.debug(f"Generated chord notes for degree {degree}: {chord_notes}")  # Log the generated chord notes
            logger.debug(f"Generated chords so far: {len(chords)}")
            chords.append(Chord(root=root_note, quality=quality_enum, notes=chord_notes))
            logger.debug(f"Chord added: {chords[-1]}")
            logger.debug(f"Generated chords so far: {chords}")  # Log the generated chords so far

        logger.info(f"Final chords generated: {len(chords)}")
        logger.debug(f"Generated chords: {[str(chord) for chord in chords]}")  # Log the generated chords before returning
        progression = ChordProgression(scale_info=self.scale_info, chords=chords)
        return progression  # Modified return statement

    def generate_random(self, length: int) -> ChordProgression:
        """Generate a random chord progression of the specified length."""
        if length <= 0:
            logger.error("Length must be a positive integer.")
            raise ValueError("Length must be a positive integer.")

        chords: List[Chord] = []
        logger.debug(f"Generating random chord progression of length: {length}")  # Log the random progression details
        for _ in range(length):
            degree = random.choice(list(self.MAJOR_SCALE_QUALITIES.keys()))
            quality = random.choice(list(self.MAJOR_SCALE_QUALITIES.values()))
            logger.debug(f"Generating random chord for degree: {degree}, quality: {quality}")

            root_note = self.scale_info.get_scale_degree_note(degree)
            if not root_note:
                logger.error(f"Invalid scale degree: {degree}")
                raise ValueError(f"Invalid scale degree: {degree}")

            logger.debug(f"Validating chord quality: {quality}")
            if quality not in [q.value for q in ChordQualityType]:
                logger.error(f"Unsupported chord type: {quality}")
                raise ValueError(f"Unsupported chord type: {quality}")
            quality_enum = ChordQualityType(quality)
            logger.debug(f"Chord quality validated: {quality_enum}")

            # Create the chord
            chord_notes = self._generate_chord_notes(root_note, quality)
            logger.debug(f"Generated chord notes for degree {degree}: {chord_notes}")  # Log the generated chord notes
            logger.debug(f"Generated chords so far: {len(chords)}")
            chords.append(Chord(root=root_note, quality=quality_enum, notes=chord_notes))
            logger.debug(f"Chord added: {chords[-1]}")
            logger.debug(f"Generated chords so far: {chords}")  # Log the generated chords so far

        logger.info(f"Final chords generated: {len(chords)}")
        logger.debug(f"Generated chords: {[str(chord) for chord in chords]}")  # Log the generated chords before returning
        progression = ChordProgression(scale_info=self.scale_info, chords=chords)
        return progression

    def generate_chord(self, numeral: str) -> Chord:
        """Generate a chord based on the given numeral."""
        logger.info("Generating chord for numeral: %s", numeral)
        degree = self._parse_numeral(numeral)

        if not degree:
            logger.error(f"Invalid numeral: {numeral}")
            raise ValueError(f"Invalid numeral: {numeral}")

        quality = self.scale_info.get_chord_quality_for_degree(degree)
        logger.debug(f"Retrieved chord quality for degree {degree}: {quality}")  # Log the retrieved quality
        logger.debug(f"Quality before validation: {quality}")  # Log the quality before validation

        if not quality:
            logger.error(f"Cannot determine chord quality for degree: {degree}")
            raise ValueError(f"Cannot determine chord quality for degree: {degree}")

        root_note = self.scale_info.get_scale_degree_note(degree)
        if not root_note:
            logger.error(f"No root note found for degree: {degree}")
            raise ValueError(f"No root note found for degree: {degree}")

        logger.debug(f"Validating chord quality: {quality}")
        if quality not in [q.value for q in ChordQualityType]:
            logger.error(f"Unsupported chord type: {quality}")
            raise ValueError(f"Unsupported chord type: {quality}")

        # Create the chord
        chord_notes = self._generate_chord_notes(root_note, quality)
        logger.debug(f"Generated chord notes for degree {degree}: {chord_notes}")
        chord = Chord(root=root_note, notes=chord_notes, quality=ChordQualityType(quality))
        logger.debug(f"Generated chord: {chord}")
        return chord

    def _parse_numeral(self, numeral: str) -> Optional[int]:
        """Parse a Roman numeral to a scale degree."""
        return RomanNumeral.to_scale_degree(numeral)  # Call the method directly on the class

    def get_scale_degree_note(self, degree: int) -> Optional[Note]:
        """Get the note for a scale degree."""
        notes = self.scale_info.get_scale_notes()
        if degree < 1 or degree > len(notes):
            return None
        return notes[degree - 1]