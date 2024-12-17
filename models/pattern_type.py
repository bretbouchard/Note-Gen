"""Module for defining musical pattern types.

This module provides definitions for various musical pattern types used in the application. It includes enumerations and classes that represent different types of musical patterns, such as rhythmic patterns, melodic patterns, and harmonic patterns.

Pattern Types
-------------

The `PatternType` enumeration defines the following musical pattern types:

- `RHYTHMIC`: Represents rhythmic patterns, which define the timing and duration of notes.
- `MELODIC`: Represents melodic patterns, which define the sequence of pitches in a melody.
- `HARMONIC`: Represents harmonic patterns, which define the combination of pitches played simultaneously.
- `ARPEGGIO`: Represents arpeggio patterns, which define the playing of notes in a chord sequentially rather than simultaneously.
- `SCALE`: Represents scale patterns, which define a series of notes in a specific order based on a musical scale.
- `CHROMATIC`: Represents chromatic patterns, which define a series of notes that include all the notes of the chromatic scale.

Usage
-----

To use the `PatternType` enumeration, simply reference the desired pattern type as follows:

```python
pattern_type = PatternType.RHYTHMIC
print(pattern_type)
```

This module is designed to be extensible, allowing for the addition of new pattern types as needed.

Note: The `PatternType` enumeration is designed to be used as a base class for other pattern types. It provides a basic structure for defining pattern types and can be extended to include additional attributes and methods as needed.

Additional pattern types can be added as needed by creating new enumeration values. For example:

```python
class PatternType(Enum):
    # ... existing pattern types ...
    NEW_PATTERN_TYPE = "new_pattern_type"
```

When adding new pattern types, be sure to update the documentation to reflect the new pattern type and its usage."""

from enum import Enum

class PatternType(str, Enum):
    """Enum representing different types of musical patterns."""
    RHYTHMIC = "rhythmic"
    MELODIC = "melodic"
    HARMONIC = "harmonic"
    ARPEGGIO = "arpeggio"
    SCALE = "scale"
    CHROMATIC = "chromatic"

    @property
    def requires_scale(self) -> bool:
        """Check if this pattern type requires a scale context."""
        return self in {
            PatternType.SCALE,
            PatternType.MELODIC,
            PatternType.ARPEGGIO
        }

    @property
    def requires_chord(self) -> bool:
        """Check if this pattern type requires a chord context."""
        return self in {PatternType.ARPEGGIO}

    @property
    def allows_repetition(self) -> bool:
        """Check if this pattern type allows note repetition."""
        return self in {
            PatternType.MELODIC,
            PatternType.RHYTHMIC
        }
