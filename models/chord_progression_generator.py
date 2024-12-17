"""Module for generating chord progressions."""
from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

import logging
logger = logging.getLogger(__name__)

from enum import Enum
from typing import Dict, List, Optional, Tuple, ClassVar
from pydantic import BaseModel, Field
from .chord import Chord, ChordQuality
from .scale_info import ScaleInfo
from .chord_progression import ChordProgression
from .note import Note

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
    scale_info: ScaleInfo
    progression_length: int = Field(default=4)
    pattern: Optional[ProgressionPattern] = None

    # Define common chord qualities for major and minor scales
    MAJOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "major",      # I
        2: "minor",      # ii
        3: "minor",      # iii
        4: "major",      # IV
        5: "major",      # V
        6: "minor",      # vi
        7: "diminished"  # vii°
    }

    MINOR_SCALE_QUALITIES: ClassVar[Dict[int, str]] = {
        1: "minor",      # i
        2: "diminished", # ii°
        3: "major",      # III
        4: "minor",      # iv
        5: "minor",      # v
        6: "major",      # VI
        7: "major"       # VII
    }

    # Define common progression patterns
    PROGRESSION_PATTERNS: ClassVar[Dict[ProgressionPattern, List[Tuple[int, str]]]] = {
        ProgressionPattern.BASIC_I_IV_V_I: [(1, "major"), (4, "major"), (5, "major"), (1, "major")],
        ProgressionPattern.POP_I_V_vi_IV: [(1, "major"), (5, "major"), (6, "minor"), (4, "major")],
        ProgressionPattern.BLUES_I_IV_I_V: [(1, "major7"), (4, "major7"), (1, "major7"), (5, "dominant7")],
        ProgressionPattern.JAZZ_ii_V_I: [(2, "minor7"), (5, "dominant7"), (1, "major7")],
        ProgressionPattern.FIFTIES_I_vi_IV_V: [(1, "major"), (6, "minor"), (4, "major"), (5, "major")],
        ProgressionPattern.CANON_I_V_vi_iii_IV_I_IV_V: [
            (1, "major"), (5, "major"), (6, "minor"), (3, "minor"),
            (4, "major"), (1, "major"), (4, "major"), (5, "major")
        ],
        ProgressionPattern.MINOR_i_iv_v: [(1, "minor"), (4, "minor"), (5, "minor")],
        ProgressionPattern.MINOR_i_VI_III_VII: [(1, "minor"), (6, "major"), (3, "major"), (7, "major")]
    }

    CHORD_INTERVALS: ClassVar[Dict[str, List[int]]] = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "diminished": [0, 3, 6],
        "major7": [0, 4, 7, 11],
        "minor7": [0, 3, 7, 10],
        "dominant7": [0, 4, 7, 10]
    }

    def get_chord_quality(self, scale_degree: int, is_minor: bool = False) -> str:
        """Get the default chord quality for a scale degree."""
        qualities = self.MINOR_SCALE_QUALITIES if is_minor else self.MAJOR_SCALE_QUALITIES
        return qualities[scale_degree]

    def _generate_chord_notes(self, root: Note, quality: str) -> List[Note]:
        intervals = self.CHORD_INTERVALS[quality]
        chord_notes = []
        for interval in intervals:
            note = root.transpose(interval)  # Assuming Note has a transpose method
            chord_notes.append(note)
        return chord_notes

    def generate(self, pattern: Optional[ProgressionPattern] = None) -> ChordProgression:
        """Generate a chord progression based on the specified pattern."""
        try:
            logger.info(f"Generating chord progression with pattern: {pattern}")
            if pattern is None:
                pattern = self.pattern
            if pattern is None:
                logger.error("Pattern is not specified.")
                raise ValueError("Pattern is not specified.")
            progression = ChordProgression(scale_info=self.scale_info)
            progression_pattern = self.PROGRESSION_PATTERNS[pattern]
            self.scale_info.compute_scale_degrees()  # Ensure this is called before generating chords
            logger.info(f"Scale degrees available: {self.scale_info.scale_degrees}")  # Log available scale degrees
            for degree, quality in progression_pattern:
                logger.info(f"Generating chord for degree: {degree}, quality: {quality}")  # Log degree and quality
                root = self.scale_info.get_scale_degree(degree)
                if root is None or not isinstance(root, Note):
                    logger.error(f"Invalid root note for degree: {degree}")
                    continue  # Skip this iteration if root is None
                chord_notes = self._generate_chord_notes(root, quality)
                if chord_notes is None or not all(isinstance(note, Note) for note in chord_notes):
                    logger.error(f"Failed to generate valid chord notes for root: {root} and quality: {quality}")
                    continue  # Skip this iteration if chord_notes is invalid
                bass = self.scale_info.get_scale_degree(degree + 1)  # Assuming bass is the next degree
                if bass is None or not isinstance(bass, Note):
                    logger.error(f"Invalid bass note for degree: {degree}")
                    continue  # Skip if bass is invalid
                if root is None or not isinstance(root, Note) or any(note is None for note in chord_notes) or bass is None or not isinstance(bass, Note):
                    logger.error(f"Invalid root or chord notes or bass for degree: {degree}")
                    continue  # Skip this iteration if root or chord_notes or bass is invalid
                chord = Chord(root=root, quality=ChordQuality(quality), notes=chord_notes, bass=bass)
                progression.add_chord(chord)
                logger.info(f"Generated chord - Root: {root}, Bass: {bass}, Chord Notes: {chord_notes}")
            return progression
        except Exception as e:
            logger.error(f"Failed to generate chord progression: {str(e)}")
            raise

    def generate_custom(self, degrees: List[int], qualities: List[str]) -> ChordProgression:
        """Generate a custom chord progression based on specified degrees and qualities."""
        try:
            logger.info(f"Generating custom progression with degrees: {degrees} and qualities: {qualities}")
            if len(degrees) != len(qualities):
                logger.error("Degrees and qualities lists must be of the same length.")
                raise ValueError("Degrees and qualities lists must be of the same length.")
            progression = ChordProgression(scale_info=self.scale_info)
            for degree, quality in zip(degrees, qualities):
                logger.info(f"Generating chord for degree: {degree}, quality: {quality}")  # Log degree and quality
                root = self.scale_info.scale_notes[degree - 1]  # Adjust for 0-indexing
                if root is None or not isinstance(root, Note):
                    logger.error(f"Invalid root note for degree: {degree}")
                    continue  # Skip this iteration if root is None
                chord_notes = self._generate_chord_notes(root, quality)
                if chord_notes is None or not all(isinstance(note, Note) for note in chord_notes):
                    logger.error(f"Failed to generate valid chord notes for root: {root} and quality: {quality}")
                    continue  # Skip this iteration if chord_notes is invalid
                if root is None or not isinstance(root, Note) or any(note is None for note in chord_notes):
                    logger.error(f"Invalid root or chord notes for degree: {degree}")
                    continue  # Skip this iteration if root or chord_notes is invalid
                chord = Chord(root=root, quality=ChordQuality(quality), notes=chord_notes, bass=root)
                progression.add_chord(chord)
                logger.info(f"Generated chord - Root: {root}, Bass: {root}, Chord Notes: {chord_notes}")
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
            import random
            progression = ChordProgression(scale_info=self.scale_info)
            for _ in range(length):
                degree = random.choice(list(self.MAJOR_SCALE_QUALITIES.keys()))
                quality = random.choice(list(self.MAJOR_SCALE_QUALITIES.values()))
                logger.info(f"Generating chord for degree: {degree}, quality: {quality}")  # Log degree and quality
                root = self.scale_info.scale_notes[degree - 1]  # Adjust for 0-indexing
                if root is None or not isinstance(root, Note):
                    logger.error(f"Invalid root note for degree: {degree}")
                    continue  # Skip this iteration if root is None
                chord_notes = self._generate_chord_notes(root, quality)
                if chord_notes is None or not all(isinstance(note, Note) for note in chord_notes):
                    logger.error(f"Failed to generate valid chord notes for root: {root} and quality: {quality}")
                    continue  # Skip this iteration if chord_notes is invalid
                if root is None or not isinstance(root, Note) or any(note is None for note in chord_notes):
                    logger.error(f"Invalid root or chord notes for degree: {degree}")
                    continue  # Skip this iteration if root or chord_notes is invalid
                chord = Chord(root=root, quality=ChordQuality(quality), notes=chord_notes, bass=root)
                progression.add_chord(chord)
                logger.info(f"Generated chord - Root: {root}, Bass: {root}, Chord Notes: {chord_notes}")
            return progression
        except Exception as e:
            logger.error(f"Failed to generate random chord progression: {str(e)}")
            raise

    def generate_chord(self, numeral: str) -> Chord:
        """Generate a chord based on the given numeral."""
        # Determine the scale degree from the numeral
        scale_degree = self._parse_numeral(numeral)
        if scale_degree is None:
            raise ValueError(f"Invalid numeral: {numeral}")

        # Determine if the chord is minor
        is_minor = numeral.islower() or 'm' in numeral

        # Get the chord quality
        quality = self.get_chord_quality(scale_degree, is_minor)

        # Generate the root note based on the scale info
        root_note = self.scale_info.root

        # Ensure root is a valid Note object
        if root_note is None or not isinstance(root_note, Note):
            logger.error(f"Invalid root note for degree: {scale_degree}")
            raise ValueError(f"Invalid root note for degree: {scale_degree}")

        # Ensure chord_notes are generated and valid
        chord_notes = self._generate_chord_notes(root_note, quality)
        if chord_notes is None or not all(isinstance(note, Note) for note in chord_notes):
            logger.error(f"Failed to generate valid chord notes for root: {root_note} and quality: {quality}")
            raise ValueError(f"Failed to generate valid chord notes for root: {root_note} and quality: {quality}")

        # Ensure root and chord_notes do not contain None values
        if root_note is None or not isinstance(root_note, Note) or any(note is None for note in chord_notes):
            logger.error(f"Invalid root or chord notes for degree: {scale_degree}")
            raise ValueError(f"Invalid root or chord notes for degree: {scale_degree}")

        # Create and return the Chord object
        return Chord(root=root_note, quality=ChordQuality(quality), notes=chord_notes)

    def _parse_numeral(self, numeral: str) -> Optional[int]:
        """Parse a Roman numeral to a scale degree."""
        if '/' in numeral:
            # Handle compound numerals (e.g., I/V)
            parts = numeral.split('/')
            return self._parse_numeral(parts[0])  # Return the first part for now

        numeral_map = {
            'I': 1, 'ii': 2, 'iii': 3, 'IV': 4, 'V': 5, 'vi': 6, 'vii': 7,
            'i': 1, 'iv': 4, 'v': 5, 'VI': 6, 'VII': 7,
            'bIII': 3, 'bVI': 6, 'bII': 2, 'bVII': 7, 'bI': 1,
            'III': 3, 'VII': 7
        }
        return numeral_map.get(numeral)