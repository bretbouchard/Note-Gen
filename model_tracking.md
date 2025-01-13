# Model Tracking for Note Gen Application

## Chord Progression Model
- **Fields**:
  - `id`: int
  - `name`: str
  - `style`: str
  - `degrees`: List[int]  # List of degrees in the progression
  - `scale_info`: ScaleInfo
  - `chords`: List[Chord]
- **Methods**:
  - `add_chord(chord: Chord)`
  - `get_chord_at(index: int)`
  - `get_all_chords()`

## Chord Quality Model
- **Fields**:
  - `quality`: ChordQualityType
- **Methods**:
  - `from_string(quality_str: str)`

## Note Model
- **Fields**:
  - `note_name`: str
  - `octave`: int
  - `duration`: float
  - `velocity`: int
  - `stored_midi_number`: Optional[int]
- **Methods**:
  - Validation methods for note_name and other fields.

## Note Event Model
- **Fields**:
  - `note`: Union[Note, ScaleDegree, Chord]
  - `position`: float
  - `duration`: float
  - `velocity`: int
  - `is_rest`: bool
- **Methods**:
  - Validation methods for position and duration.

## Note Pattern Model
- **Fields**:
  - `id`: int
  - `pattern`: str
  - `name`: str
  - `data`: List[Union[int, List[int]]]
  - `notes`: List[Note]
  - `description`: str
  - `tags`: List[str]
- **Methods**:
  - Validation methods for notes and data.

## Note Sequence Model
- **Fields**:
  - `notes`: List[Union[Note, int]]
  - `events`: List[NoteEvent]
  - `duration`: float
- **Methods**:
  - Validation methods for notes.

## Rhythm Pattern Model
- **Fields**:
  - `id`: int
  - `pattern`: str
  - `name`: str
  - `data`: RhythmPatternData
  - `description`: str
  - `tags`: List[str]
  - `complexity`: float
  - `style`: Optional[str]
- **Methods**:
  - Validation methods for name and data.

## Key Model
- **Fields**:
  - `id`: int
  - `name`: str

## Scale Model
- **Fields**:
  - `id`: int
  - `name`: str
  - `root`: Note
  - `scale_type`: ScaleType
- **Methods**:
  - Methods for getting notes and scale degrees.

## Scale Degree Model
- **Fields**:
  - `degree`: int
  - `note`: Note
  - `value`: Optional[str]
  - `midi_number`: int
- **Methods**:
  - Validation methods for degree.

## Scale Info Model
- **Fields**:
  - `root`: Note
  - `scale_type`: ScaleType
- **Methods**:
  - Methods for computing scale degrees and retrieving notes.

## Interval Model
- **Fields**:
  - `id`: int
  - `name`: str

## Roman Numeral Model
- **Fields**:
  - `ROMAN_TO_INT`: Mapping of Roman numerals to integers.
  - `INT_TO_ROMAN`: Reverse mapping from integers to Roman numerals.
- **Methods**:
  - `from_scale_degree(degree: int, quality: ChordQualityType)`
  - `to_scale_degree(numeral: str)`

## Pattern Interpreter Model
- **Fields**:
  - `scale`: Scale
  - `pattern`: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]]
  - `_current_index`: int
- **Methods**:
  - `__init__(scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]])`

## Scale Pattern Interpreter
- **Methods**:
  - `interpret(self, pattern: Sequence[Union[int, str, Note, ScaleDegree]], chord: Any, scale_info: Any)`

## Arpeggio Pattern Interpreter
- **Methods**:
  - `__init__(scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]])`

## Melodic Pattern Interpreter
- **Methods**:
  - `__init__(scale: Scale, pattern: Sequence[Union[int, str, Note, ScaleDegree, Dict[str, Any]]])`

## Chord Progression Generator Model
- **Fields**:
  - `scale_info`: ScaleInfo
  - `progression_length`: int
  - `pattern`: Optional[List[str]]
- **Methods**:
  - Class variables for common chord qualities.

## Enums
- **Classes**:
  - `AccidentalType`: Enum for accidentals (natural, sharp, flat).
  - `ChordQualityType`: Enum for chord qualities (major, minor, diminished).
  - `ScaleType`: Enum for scale types (major, natural minor).

## Musical Elements Model
- **Classes**:
  - `ChordQuality`: Model for chord quality with fields for different qualities.
  - `Chord`: Model for a musical chord with fields for root, quality, and notes.

## Pattern Type Model
- **Classes**:
  - `PatternType`: Enum for different musical pattern types (ascending, descending, random).

## Patterns Model
- **Classes**:
  - `RhythmPatternData`: Data structure for rhythm patterns with fields for notes, duration, and time signature.

## Presets
- **Common Chord Progressions**: Dict[str, List[str]]
- **Default Values**:
  - `DEFAULT_KEY`: "C"
  - `DEFAULT_SCALE_TYPE`: "major"
  - `DEFAULT_CHORD_PROGRESSION`: "I-IV-V-I"
  - `DEFAULT_NOTE_PATTERN`: "Simple Triad"
  - `DEFAULT_RHYTHM_PATTERN`: "quarter_notes"

## Enums
- **Chord Quality**: Enum for different chord qualities (e.g., Major, Minor)
- **Scale Types**: Enum for different scale types (e.g., Major, Minor)

## Additional Notes
- Ensure all models are aligned with the API requirements and are testable.
- Update tests to reflect any changes in the models or API endpoints.
