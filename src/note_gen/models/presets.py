# src/note_gen/models/presets.py

"""Presets for chord progressions, note patterns, and rhythm patterns."""

from typing import Dict, List
from pydantic import BaseModel, ConfigDict

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.musical_elements import Note
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import (
    RhythmPattern,
    RhythmPatternData,
    RhythmNote,
)
from src.note_gen.models.scale import Scale
from src.note_gen.models.scale_info import ScaleInfo 

# Default values for musical components
DEFAULT_KEY = "C"
DEFAULT_SCALE_TYPE = "major"
DEFAULT_CHORD_PROGRESSION = "I-IV-V-I"
DEFAULT_NOTE_PATTERN = "Simple Triad"
DEFAULT_RHYTHM_PATTERN = "quarter_notes"
DEFAULT_RHYTHM_PATTERN_NAME = "Quarter Notes"


class Presets(BaseModel):
    # Define your fields here
    model_config = ConfigDict(arbitrary_types_allowed=True)


# Common chord progressions in Roman numeral notation
COMMON_PROGRESSIONS: Dict[str, List[str]] = {
    # Standard Progressions
    "I-IV-V": ["I", "IV", "V"],
    "I-V-vi-IV/Pop Ballad/Pop I-V-vi-IV": ["I", "V", "vi", "IV"],
    "ii-V-I": ["ii", "V", "I"],
    "I-vi-IV-V/50s Doo-Wop": ["I", "vi", "IV", "V"],
    "vi-IV-I-V/Modern Pop": ["vi", "IV", "I", "V"],
    "I-V-vi-iii-IV-I-IV-V/Pop Canon": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],
    "I-IV-V-I": ["I", "IV", "V", "I"],
    # Jazz Progressions
    "Autumn Leaves": ["ii7", "V7", "Imaj7", "IV7", "vii°7", "III7", "vi7"],
    "Giant Steps": ["Imaj7", "III7", "vi7", "II7", "V7", "VII7", "III7"],
    "12-Bar Blues": [
        "I7",
        "I7",
        "I7",
        "I7",
        "IV7",
        "IV7",
        "I7",
        "I7",
        "V7",
        "IV7",
        "I7",
        "V7",
    ],
    "i vi ii V": ["i", "vi", "ii", "V"],
    "Minor Scale Ascension": ["i", "ii", "III", "iv", "v", "VI", "VII", "i"],
    "II-V-I in C Major": ["Dm7", "G7", "Cmaj7"],
    "II-V-I in G Major": ["Am7", "D7", "Gmaj7"],
    "I-VI-II-V/Ladybird": ["Imaj7", "vi7", "ii7", "V7"],
    "Rhythm Changes": ["Imaj7", "VI7", "ii7", "V7", "Imaj7", "VI7", "ii7", "V7"],
    "Jazz Blues in F": ["F7", "Bb7", "F7", "D7", "G7", "C7"],
    "Minor II-V-I": ["ii°7", "V7", "i"],
    "Descending II-Vs": ["ii7", "V7", "ii7", "V7"],
    "Extended Turnaround": ["I", "vi", "ii", "V", "I"],
    "Backdoor Progression": ["I", "bIII", "bVII", "IV"],
    "Modal Interchange": ["I", "bIII", "iv", "V"],
    "Altered Dominant": ["V7alt", "I"],
    "Parallel Minor": ["I", "vi", "iv", "V"],
    "Half-Step II-V": ["ii", "V", "ii♭5", "V♭5"],
    "Coltrane Changes": ["I", "VI7", "ii7", "V7", "I♭7", "VI♭7", "ii♭7", "V♭7"],
    "Pedal Point": ["I", "I/V", "V", "I"],
    "III-VI-II-V": ["iii", "vi", "ii", "V"],
    "Tritone Substitution": ["V7", "V7alt", "I"],
    "Minor Blues": ["im7", "iv7", "v7", "im7"],
    "Funk Groove": ["I7", "IV7", "V7"],
    "I7-IV7-V7 Turnaround": ["I7", "IV7", "V7"],
    "Bird Blues": ["I7", "VI7", "ii7", "V7"],
    "So What": ["Dm7", "Dm7", "Ebm7", "Ebm7"],
    "Giant Steps Bridge": ["B", "D7", "G", "Bb7", "Eb", "F#7"],
    "Misty": ["i", "vi", "ii", "V"],
    # Pop Progressions
    "Rock Power": ["I", "V", "vi"],
    "Andalusian Cadence": ["Am", "G", "F", "E"],
    "EDM Build": ["i", "V", "vi", "III"],
    "Pop Minor": ["i", "VI", "III", "VII"],
}

# Note patterns
NOTE_PATTERNS: Dict[str, List[int]] = {
    "Simple Triad": [0, 2, 4],
    "Ascending Scale": [0, 1, 2, 3, 4, 5, 6, 7],
    "Descending Scale": [7, 6, 5, 4, 3, 2, 1, 0],
    "Arpeggio": [0, 2, 4, 7],
    "Pentatonic": [0, 2, 4, 7, 9],
}

# Rhythm patterns
RHYTHM_PATTERNS: Dict[str, RhythmPatternData] = {
    "quarter_notes": RhythmPatternData(
        notes=[
            RhythmNote(position=float(0.0), duration=float(1.0)),
            RhythmNote(position=float(1.0), duration=float(1.0)),
            RhythmNote(position=float(2.0), duration=float(1.0)),
            RhythmNote(position=float(3.0), duration=float(1.0)),
        ]
    ),
    "eighth_notes": RhythmPatternData(
        notes=[
            RhythmNote(position=float(0.0), duration=float(0.5)),
            RhythmNote(position=float(0.5), duration=float(0.5)),
            RhythmNote(position=float(1.0), duration=float(0.5)),
            RhythmNote(position=float(1.5), duration=float(0.5)),
            RhythmNote(position=float(2.0), duration=float(0.5)),
            RhythmNote(position=float(2.5), duration=float(0.5)),
        ]
    ),
    "syncopated": RhythmPatternData(
        notes=[
            RhythmNote(position=float(0.0), duration=float(1.5)),
            RhythmNote(position=float(1.5), duration=float(1.0)),
            RhythmNote(position=float(2.0), duration=float(0.5)),
        ]
    ),
    "dotted_quarter": RhythmPatternData(
        notes=[
            RhythmNote(position=float(0.0), duration=float(1.5)),
            RhythmNote(position=float(1.5), duration=float(1.5)),
            RhythmNote(position=float(3.0), duration=float(1.0)),
        ]
    ),
}

def get_default_chord_progression(root_note: Note, scale: Scale) -> ChordProgression:
    """Get the default chord progression."""
    from .chord_progression_generator import ChordProgressionGenerator

    scale_info = ScaleInfo(root=root_note, scale_type=scale.scale_type)
    scale_info.compute_scale_degrees()  # Ensure degrees are populated
    generator = ChordProgressionGenerator(scale_info=scale_info)

    numerals = COMMON_PROGRESSIONS[DEFAULT_CHORD_PROGRESSION]
    chords = []
    for numeral in numerals:
        chord = generator.generate_chord(numeral)
        chords.append(chord)
    return ChordProgression(scale_info=scale_info, chords=chords)

def get_default_note_pattern() -> NotePattern:
    """Get the default note pattern."""
    return NotePattern(
        name=DEFAULT_NOTE_PATTERN, data=NOTE_PATTERNS[DEFAULT_NOTE_PATTERN]
    )

def get_default_rhythm_pattern() -> RhythmPattern:
    return RhythmPattern(
        name=DEFAULT_RHYTHM_PATTERN_NAME,
        data=RHYTHM_PATTERNS["quarter_notes"]
    )

def get_available_chord_progressions() -> List[str]:
    """Get a list of available chord progression names."""
    return list(COMMON_PROGRESSIONS.keys())

def get_available_note_patterns() -> List[str]:
    """Get a list of available note pattern names."""
    return list(NOTE_PATTERNS.keys())

def get_available_rhythm_patterns() -> List[str]:
    """Get a list of available rhythm pattern names."""
    return list(RHYTHM_PATTERNS.keys())