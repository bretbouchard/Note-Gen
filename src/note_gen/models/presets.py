# src/note_gen/models/presets.py

"""Presets for chord progressions, note patterns, and rhythm patterns."""

from typing import Dict, List, Any
from pydantic import BaseModel
import uuid

from src.note_gen.models.chord_progression import ChordProgression
from src.note_gen.models.chord import Chord
from src.note_gen.models.note import Note
from src.note_gen.models.note_pattern import NotePattern
from src.note_gen.models.rhythm_pattern import (RhythmPattern,RhythmPatternData,RhythmNote,)
from src.note_gen.models.scale import Scale
from src.note_gen.models.enums import ScaleType, ChordQualityType
from src.note_gen.models.scale_info import ScaleInfo 
from src.note_gen.models.roman_numeral import RomanNumeral

# Default values for musical components
DEFAULT_KEY = "C"
DEFAULT_SCALE_TYPE = ScaleType.MAJOR
DEFAULT_CHORD_PROGRESSION = "I-IV-V"
DEFAULT_NOTE_PATTERN = "Simple Triad"
DEFAULT_RHYTHM_PATTERN = "Basic Rhythm"
DEFAULT_RHYTHM_PATTERN_NAME = "Basic"

# Common chord progressions in Roman numeral notation
COMMON_PROGRESSIONS: Dict[str, List[str]] = {
    # Standard Progressions
    "I-IV-V": ["I", "IV", "V"], 
    "Pop Ballad_I-V-vi-IV": ["I", "V", "vi", "IV"],
    "ii-V-I": ["ii", "V", "I"],
    "I-vi-IV-V/50s Doo-Wop": ["I", "vi", "IV", "V"], 
    "vi-IV-I-V/Modern Pop": ["vi", "IV", "I", "V"],
    "I-V-vi-iii-IV-I-IV-V/Pop Canon": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],
    "I-IV-V-I": ["I", "IV", "V", "I"],
    # Jazz Progressions
    "Autumn Leaves": ["ii7", "V7", "Imaj7", "IV7", "vii°7", "III7", "vi7"],
    "Giant Steps": ["Imaj7", "III7", "vi7", "II7", "V7", "VII7", "III7"],
    "12-Bar Blues": ["I7","I7","I7","I7","IV7","IV7","I7","I7","V7","IV7","I7","V7"],
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
    "Rock Power": ["I", "V", "vi"],
    "Andalusian Cadence": ["Am", "G", "F", "E"],
    "EDM Build": ["i", "V", "vi", "III"],
    "Pop Minor": ["i", "VI", "III", "VII"],
}

class Presets(BaseModel):
    common_progressions: Dict[str, List[str]] = COMMON_PROGRESSIONS
    default_key: str = DEFAULT_KEY
    default_scale_type: ScaleType = DEFAULT_SCALE_TYPE

    @classmethod
    def load(cls) -> List['Presets']:
        # Implement loading logic here
        presets = []
        if cls.common_progressions:
            presets.append(cls())
        return presets  # Example return, replace with actual loading logic

    def get_default_chord_progression(self, root_note: Note, scale: Scale) -> ChordProgression:
        """Get the default chord progression."""
        chords: List[Chord] = []  # Initialize an empty list of Chord instances if needed
        complexity: float = 0.5  # Define complexity here
        
        # Ensure all required fields are provided
        scale_info: ScaleInfo = ScaleInfo(
            scale_type=scale.scale_type,
            root=scale.root  # Ensure this is included
        )
        
        return ChordProgression(
            name="Default Progression",
            root=root_note,
            scale=scale,
            progression=DEFAULT_CHORD_PROGRESSION,
            chords=chords,
            complexity=complexity,
            scale_info=scale_info
        )

    def get_default_note_pattern(self) -> NotePattern:
        """Get the default note pattern."""
        return NotePattern(
            id=uuid.uuid4(),
            name="Default Pattern",
            pattern=[],
            pattern_type="simple",
            description="A simple pattern",
            tags=["default"],
            complexity=0.5,
            data=NOTE_PATTERNS[DEFAULT_NOTE_PATTERN]
        )

    def get_default_rhythm_pattern(self) -> RhythmPattern:
        """Get the default rhythm pattern."""
        return RhythmPattern(
            name="Default Rhythm Pattern",
            data=RHYTHM_PATTERNS[DEFAULT_RHYTHM_PATTERN],
            complexity=0.5
        )

    def get_available_chord_progressions(self) -> List[str]:
        """Get a list of available chord progression names."""
        return list(COMMON_PROGRESSIONS.keys())

    def get_available_note_patterns(self) -> List[str]:
        """Get a list of available note pattern names."""
        return list(NOTE_PATTERNS.keys())

    def get_available_rhythm_patterns(self) -> List[str]:
        """Get a list of available rhythm pattern names."""
        return list(RHYTHM_PATTERNS.keys())

# Note patterns
NOTE_PATTERNS: Dict[str, Dict[str, Any]] = {
    "Simple Triad": {
        "index": 1,
        "pattern": [0, 2, 4],
        "tags": ["triad", "basic"],
        "complexity": 0.5,
        "description": "A simple triad pattern."
    },
    "Ascending Scale": {
        "index": 2,
        "pattern": [0, 1, 2, 3, 4, 5, 6, 7],
        "tags": ["scale", "ascending"],
        "complexity": 0.3,
        "description": "An ascending scale pattern."
    },
    "Descending Scale": {
        "index": 3,
        "pattern": [7, 6, 5, 4, 3, 2, 1, 0],
        "tags": ["scale", "descending"],
        "complexity": 0.3,
        "description": "A descending scale pattern." 
    },
    "Arpeggio": {
        "index": 4,
        "pattern": [0, 2, 4, 7],
        "tags": ["arpeggio", "broken chord"],
        "complexity": 0.4,
        "description": "An arpeggio pattern."
    },
    "Pentatonic": {
        "index": 5,
        "pattern": [0, 2, 4, 7, 9],
        "tags": ["pentatonic", "scale"],
        "complexity": 0.4,
        "description": "A pentatonic scale pattern."
    },
}

# Rhythm patterns
RHYTHM_PATTERNS: Dict[str, Dict[str, Any]] = {
    "Basic Rhythm": {
        "index": 1,
        "pattern": [1, -1, 1, -1],
        "tags": ["basic", "rhythm"],
        "complexity": 0.2,
        "description": "A simple on-off rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 1, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 2, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 3, "duration": 1.0, "velocity": 100, "is_rest": False}
        ]
    },
    "Swing Rhythm": {
        "index": 2,
        "pattern": [1, -0.5, 1, -0.5],
        "tags": ["swing", "rhythm"],
        "complexity": 0.3,
        "description": "A swing rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 0.5, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 1, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 1.5, "duration": 0.5, "velocity": 100, "is_rest": False}
        ]
    },
    "Rock Rhythm": {
        "index": 3,
        "pattern": [1, -1, 1, -0.5],
        "tags": ["rock", "rhythm"],
        "complexity": 0.2,
        "description": "A simple rock rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 1, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 2, "duration": 0.5, "velocity": 100, "is_rest": False}
        ]
    },
    "Waltz Rhythm": {
        "index": 4,
        "pattern": [1, -1, 1, -1],
        "tags": ["waltz", "rhythm"],
        "complexity": 0.3,
        "description": "A waltz rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 1, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 2, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 3, "duration": 1.0, "velocity": 100, "is_rest": False}
        ]
    },
    "Bossa Nova": {
        "index": 5,
        "pattern": [1, -1, 1, -1],
        "tags": ["bossa nova", "rhythm"],
        "complexity": 0.3,
        "description": "A bossa nova rhythm pattern.",
        "notes": [
            {"position": 0.0, "duration": 1.0, "velocity": 100, "is_rest": False},
            {"position": 1.0, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 1.5, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 2.0, "duration": 0.5, "velocity": 100, "is_rest": False}
        ]
    },
    "Latin Rhythm": {
        "index": 6,
        "pattern": [1, -1, 1, -1],
        "tags": ["latin", "rhythm"],
        "complexity": 0.3,
        "description": "A Latin-inspired rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 1, "velocity": 100, "is_rest": False},
            {"position": 1, "duration": 0.25, "velocity": 100, "is_rest": False},
            {"position": 1.5, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 2.0, "duration": 0.5, "velocity": 100, "is_rest": False}
        ]
    },
    "Funk Rhythm": {
        "index": 7,
        "pattern": [1, -1, 1, -1],
        "tags": ["funk", "rhythm"],
        "complexity": 0.3,
        "description": "A funk-inspired rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 0.5, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 1.5, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 2.0, "duration": 0.5, "velocity": 100, "is_rest": False}
        ]
    },
    "Jazz Rhythm": {
        "index": 8,
        "pattern": [1, -1, 1, -1],
        "tags": ["jazz", "rhythm"],
        "complexity": 0.3,
        "description": "A jazz-inspired rhythm pattern.",
        "notes": [
            {"position": 0, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 0.5, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 1.0, "duration": 0.5, "velocity": 100, "is_rest": False},
            {"position": 1.5, "duration": 0.5, "velocity": 100, "is_rest": False}
        ]
    }
} 

# Chord progressions
CHORD_PROGRESSIONS: Dict[str, Dict[str, Any]] = {
    "I-IV-V": {
        "index": 1,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["popular", "progression"],
        "complexity": 0.5,
        "description": "A common chord progression in popular music."
    },
    "Pop Ballad_I-V-vi-IV": {
        "index": 2,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["pop", "ballad"],
        "complexity": 0.5,
        "description": "A popular pop ballad progression."
    },
    "ii-V-I": {
        "index": 3,
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "progression"],
        "complexity": 0.6,
        "description": "A common ii-V-I progression in jazz music."
    },
    "I-vi-IV-V (50s Doo-Wop)": {
        "index": 4,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["doo-wop", "classic"],
        "complexity": 0.5,
        "description": "A classic 50s Doo-Wop progression."
    },
    "vi-IV-I-V (Modern Pop)": {
        "index": 5,
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["modern", "pop"],
        "complexity": 0.5,
        "description": "A common modern pop progression."
    },
    "I-V-vi-iii-IV-I-IV-V (Pop Canon)": {
        "index": 6,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["pop", "canon"],
        "complexity": 0.5,
        "description": "A popular pop canon progression."
    },
    "I-IV-V-I": {
        "index": 7,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic I-IV-V-I progression."
    },
    "ii-V-I": {
        "index": 8,
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "progression"],
        "complexity": 0.6,
        "description": "A common ii-V-I progression in jazz music."
    },
    "I-V-ii-V (Classic)": {
        "index": 9,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic I-V-ii-V progression."
    },
    "I-vi-ii-V (Classic)": {
        "index": 10,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic I-vi-ii-V progression."
    },
    "IV-I-ii-V (Classic)": {
        "index": 11,
        "chords": [
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["classic", "progression"],
        "complexity": 0.5,
        "description": "A classic IV-I-ii-V progression."
    },
    "Rock Power": {
        "index": 12,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["rock", "power"],
        "complexity": 0.5,
        "description": "A simple rock power progression."
    },
    "Andalusian Cadence": {
        "index": 13,
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["andalusian", "cadence"],
        "complexity": 0.5,
        "description": "A classic Andalusian cadence."
    },
    "EDM Build": {
        "index": 14,
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C#", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G#", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["edm", "build"],
        "complexity": 0.5,
        "description": "An EDM build progression."
    },
    "Pop Minor": {
        "index": 15,
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F#", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "C#", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G#", "octave": 4}, "quality": "MAJOR"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["pop", "minor"],
        "complexity": 0.5,
        "description": "A common pop minor progression."
    },
    "Funk Groove": {
        "index": 16,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["funk", "groove"],
        "complexity": 0.5,
        "description": "A funky groove progression."
    },
    "I7-IV7-V7 Turnaround": {
        "index": 17,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["turnaround", "classic"],
        "complexity": 0.5,
        "description": "A classic I7-IV7-V7 turnaround."
    },
    "Bird Blues": {
        "index": 18,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "blues"],
        "complexity": 0.5,
        "description": "A classic Bird blues progression."
    },
    "So What": {
        "index": 19,
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"}
        ],
        "key": "D",
        "scale_type": "MINOR",
        "tags": ["jazz", "so what"],
        "complexity": 0.5,
        "description": "The famous So What progression."
    },
    "Giant Steps Bridge": {
        "index": 20,
        "chords": [
            {"root": {"note_name": "B", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "Bb", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F#", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "B",
        "scale_type": "MAJOR",
        "tags": ["jazz", "giant steps"],
        "complexity": 0.5,
        "description": "The bridge of the Giant Steps progression."
    },
    "Misty": {
        "index": 21,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MINOR",
        "tags": ["jazz", "misty"],
        "complexity": 0.5,
        "description": "The Misty progression."
    }
}

CHORD_PROGRESSIONS.update({
    "progression_1": {
        "index": 11,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR"}
        ]
    }
})

CHORD_PROGRESSIONS.update({
    "Minor Blues": {
        "index": 33,
        "chords": [
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "E", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR7"}
        ],
        "key": "A",
        "scale_type": "MINOR",
        "tags": ["blues", "minor"],
        "complexity": 0.5,
        "description": "A common minor blues progression."
    },
    "Funk Groove": {
        "index": 34,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["funk", "groove"],
        "complexity": 0.5,
        "description": "A funky groove progression."
    },
    "I7-IV7-V7 Turnaround": {
        "index": 35,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "F", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["turnaround", "classic"],
        "complexity": 0.5,
        "description": "A classic I7-IV7-V7 turnaround."
    },
    "Bird Blues": {
        "index": 36,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MAJOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT7"}
        ],
        "key": "C",
        "scale_type": "MAJOR",
        "tags": ["jazz", "blues"],
        "complexity": 0.5,
        "description": "A classic Bird blues progression."
    },
    "So What": {
        "index": 37,
        "chords": [
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MINOR7"}
        ],
        "key": "D",
        "scale_type": "MINOR",
        "tags": ["jazz", "so what"],
        "complexity": 0.5,
        "description": "The famous So What progression."
    },
    "Giant Steps Bridge": {
        "index": 38,
        "chords": [
            {"root": {"note_name": "B", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "Bb", "octave": 4}, "quality": "DOMINANT"},
            {"root": {"note_name": "Eb", "octave": 4}, "quality": "MAJOR"},
            {"root": {"note_name": "F#", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "B",
        "scale_type": "MAJOR",
        "tags": ["jazz", "giant steps"],
        "complexity": 0.5,
        "description": "The bridge of the Giant Steps progression."
    },
    "Misty": {
        "index": 39,
        "chords": [
            {"root": {"note_name": "C", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "A", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "D", "octave": 4}, "quality": "MINOR"},
            {"root": {"note_name": "G", "octave": 4}, "quality": "DOMINANT"}
        ],
        "key": "C",
        "scale_type": "MINOR",
        "tags": ["jazz", "misty"],
        "complexity": 0.5,
        "description": "The Misty progression."
    }
})

def get_default_chord_progression(root_note: Note, scale: Scale) -> ChordProgression:
    """Get the default chord progression."""
    from .chord_progression_generator import ChordProgressionGenerator
    
    # Ensure scale_type is of type ScaleType
    scale_info = ScaleInfo(
        root=root_note, 
        scale_type=ScaleType(scale.scale_type) if isinstance(scale.scale_type, str) and scale.scale_type in [ScaleType.MAJOR, ScaleType.MINOR] else ScaleType.MAJOR
    )

    scale_info.compute_scale_degrees()  # Ensure degrees are populated
    
    # Create a ChordProgressionGenerator with all required arguments
    generator = ChordProgressionGenerator( 
        scale_info=scale_info,  
        name="Default Progression",
        chords=[],
        key=scale_info.root.note_name, 
        scale_type=ScaleType(scale.scale_type) if isinstance(scale.scale_type, str) and scale.scale_type in [ScaleType.MAJOR, ScaleType.MINOR] else ScaleType.MAJOR
    )

    numerals = COMMON_PROGRESSIONS[DEFAULT_CHORD_PROGRESSION]
    chords = []
    for numeral in numerals:  
        note = RomanNumeral.convert_to_note(numeral, scale)  # New logic using RomanNumeral
        chord = generator.generate_chord(note, quality=ChordQualityType.MAJOR)  # Provide a quality argument
        chords.append(chord)
    
    return ChordProgression(
        name="Default Progression",
        root=root_note,
        scale=scale,
        progression=DEFAULT_CHORD_PROGRESSION,
        chords=chords,
        complexity=0.5,
        scale_info=scale_info
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
