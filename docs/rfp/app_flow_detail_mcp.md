# Note-Gen MCP Server: Detailed Flow

This document provides a detailed technical breakdown of the Note-Gen MCP (Model-Controller-Presenter) Server architecture, including data types, component interactions, and implementation details.

## Data Types and Models

### Core Models

1. **Note**
   ```python
   class Note(BaseModel):
       pitch: str  # e.g., "C", "D#"
       octave: int  # e.g., 4, 5
       duration: float = 1.0  # in beats
       velocity: int = 100  # MIDI velocity (0-127)
       position: float = 0.0  # position in beats
       stored_midi_number: Optional[int] = None
   ```

2. **NotePattern**
   ```python
   class NotePatternData(BaseModel):
       key: str = "C"
       root_note: str = "C"
       scale_type: ScaleType = ScaleType.MAJOR
       direction: PatternDirection = PatternDirection.UP
       octave: int = 4
       octave_range: Tuple[int, int] = (3, 5)
       intervals: List[int] = []

   class NotePattern(BaseModel):
       id: Optional[str] = None
       name: str
       pattern: List[Note]
       data: NotePatternData
       tags: List[str] = []
       skip_validation: bool = False
   ```

3. **RhythmPattern**
   ```python
   class RhythmNote(BaseModel):
       position: float = 0.0  # in beats
       duration: float = 1.0  # in beats
       velocity: int = 100  # MIDI velocity (0-127)
       accent: bool = False

   class RhythmPattern(BaseModel):
       id: Optional[str] = None
       name: str
       pattern: List[RhythmNote]
       time_signature: Tuple[int, int] = (4, 4)
       total_duration: float = 4.0  # in beats
       style: str = "basic"
       description: str = ""
       swing_enabled: bool = False
   ```

4. **ChordProgression**
   ```python
   class ChordProgressionData(BaseModel):
       key: str = "C"
       scale_type: ScaleType = ScaleType.MAJOR
       time_signature: Tuple[int, int] = (4, 4)
       tempo: int = 120

   class ChordProgression(BaseModel):
       id: Optional[str] = None
       name: str
       progression: List[Chord]
       data: ChordProgressionData
       tags: List[str] = []
   ```

5. **Sequence**
   ```python
   class Sequence(BaseModel):
       id: Optional[str] = None
       name: str
       chord_progression_id: str
       note_pattern_ids: List[str]
       rhythm_pattern_ids: List[str]
       data: Dict[str, Any] = {}
       tags: List[str] = []
   ```

## Repository Layer

### MongoDB Repositories

1. **NotePatternRepository**
   ```python
   class NotePatternRepository(MongoDBRepository[NotePattern]):
       def __init__(self, db: AsyncIOMotorDatabase):
           super().__init__(db, "note_patterns", NotePattern)
   ```

2. **RhythmPatternRepository**
   ```python
   class RhythmPatternRepository(MongoDBRepository[RhythmPattern]):
       def __init__(self, db: AsyncIOMotorDatabase):
           super().__init__(db, "rhythm_patterns", RhythmPattern)
   ```

3. **ChordProgressionRepository**
   ```python
   class ChordProgressionRepository(MongoDBRepository[ChordProgression]):
       def __init__(self, db: AsyncIOMotorDatabase):
           super().__init__(db, "chord_progressions", ChordProgression)
   ```

4. **SequenceRepository**
   ```python
   class SequenceRepository(MongoDBRepository[Sequence]):
       def __init__(self, db: AsyncIOMotorDatabase):
           super().__init__(db, "sequences", Sequence)
   ```

## Controller Layer

### PatternController

```python
class PatternController:
    def __init__(
        self,
        note_pattern_repository: NotePatternRepository,
        rhythm_pattern_repository: RhythmPatternRepository
    ):
        self.note_pattern_repository = note_pattern_repository
        self.rhythm_pattern_repository = rhythm_pattern_repository

    async def get_note_patterns(self) -> List[NotePattern]:
        return await self.note_pattern_repository.find_all()

    async def get_rhythm_patterns(self) -> List[RhythmPattern]:
        return await self.rhythm_pattern_repository.find_all()

    async def create_note_pattern(self, pattern: NotePattern) -> NotePattern:
        return await self.note_pattern_repository.save(pattern)

    async def create_rhythm_pattern(self, pattern: RhythmPattern) -> RhythmPattern:
        return await self.rhythm_pattern_repository.save(pattern)
```

### ChordProgressionController

```python
class ChordProgressionController:
    def __init__(self, chord_progression_repository: ChordProgressionRepository):
        self.chord_progression_repository = chord_progression_repository

    async def get_chord_progressions(self) -> List[ChordProgression]:
        return await self.chord_progression_repository.find_all()

    async def create_chord_progression(self, progression: ChordProgression) -> ChordProgression:
        return await self.chord_progression_repository.save(progression)
```

### ImportExportController

```python
class ImportExportController:
    def __init__(
        self,
        chord_progression_repository: ChordProgressionRepository,
        note_pattern_repository: NotePatternRepository,
        rhythm_pattern_repository: RhythmPatternRepository,
        sequence_repository: SequenceRepository
    ):
        self.chord_progression_repository = chord_progression_repository
        self.note_pattern_repository = note_pattern_repository
        self.rhythm_pattern_repository = rhythm_pattern_repository
        self.sequence_repository = sequence_repository

    async def export_chord_progressions(self, format: str = "json") -> bytes:
        progressions = await self.chord_progression_repository.find_all()
        if format == "json":
            return self._export_to_json(progressions)
        elif format == "csv":
            return self._export_to_csv(progressions)
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def import_chord_progressions(self, data: bytes, format: str = "json") -> int:
        if format == "json":
            return await self._import_from_json(data, self.chord_progression_repository)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

## Presenter Layer

### PatternPresenter

```python
class PatternPresenter:
    @staticmethod
    def present_note_patterns(patterns: List[NotePattern]) -> Dict[str, Any]:
        return {
            "patterns": [PatternPresenter.present_note_pattern(pattern) for pattern in patterns]
        }

    @staticmethod
    def present_note_pattern(pattern: NotePattern) -> Dict[str, Any]:
        return {
            "id": pattern.id,
            "name": pattern.name,
            "pattern": [PatternPresenter.present_note(note) for note in pattern.pattern],
            "data": pattern.data.model_dump(),
            "tags": pattern.tags
        }

    @staticmethod
    def present_note(note: Note) -> Dict[str, Any]:
        return {
            "pitch": note.pitch,
            "octave": note.octave,
            "duration": note.duration,
            "velocity": note.velocity,
            "position": note.position
        }
```

## API Endpoints

### Pattern Endpoints

```python
@router.get("/note-patterns", response_model=Dict[str, List[Dict[str, Any]]])
async def get_note_patterns(pattern_controller: PatternController = Depends(get_pattern_controller)):
    patterns = await pattern_controller.get_note_patterns()
    return PatternPresenter.present_note_patterns(patterns)

@router.post("/note-patterns", response_model=Dict[str, Any])
async def create_note_pattern(
    pattern: NotePattern,
    pattern_controller: PatternController = Depends(get_pattern_controller)
):
    created_pattern = await pattern_controller.create_note_pattern(pattern)
    return PatternPresenter.present_note_pattern(created_pattern)
```

## Detailed Flow Examples

### Creating a Note Pattern

1. Client sends POST request to `/api/v1/patterns/note-patterns` with pattern data
2. FastAPI validates request using `NotePattern` Pydantic model
3. Request is routed to `create_note_pattern` endpoint
4. `PatternController.create_note_pattern` method is called
5. Controller calls `NotePatternRepository.save` to store pattern in MongoDB
6. `PatternPresenter.present_note_pattern` formats the response
7. JSON response is returned to client

### Exporting Chord Progressions

1. Client sends GET request to `/api/v1/import-export/export/chord-progressions?format=json`
2. Request is routed to `export_chord_progressions` endpoint
3. `ImportExportController.export_chord_progressions` method is called
4. Controller calls `ChordProgressionRepository.find_all` to retrieve all progressions
5. Controller formats progressions as JSON using `_export_to_json` method
6. Binary response is returned to client

## AI Integration Example

```python
@router.post("/ai/generate-sequence")
async def generate_sequence(
    request: Dict[str, Any],
    pattern_controller: PatternController = Depends(get_pattern_controller),
    chord_progression_controller: ChordProgressionController = Depends(get_chord_progression_controller)
):
    # Get patterns and progressions
    note_patterns = await pattern_controller.get_note_patterns()
    rhythm_patterns = await pattern_controller.get_rhythm_patterns()
    chord_progressions = await chord_progression_controller.get_chord_progressions()
    
    # Apply AI-driven selection and transformation
    selected_patterns = ai_select_patterns(note_patterns, request)
    selected_rhythms = ai_select_rhythms(rhythm_patterns, request)
    selected_progression = ai_select_progression(chord_progressions, request)
    
    # Generate sequence
    sequence = generate_sequence_from_components(
        selected_patterns, 
        selected_rhythms, 
        selected_progression,
        request
    )
    
    return SequencePresenter.present_sequence(sequence)
```

## Next Steps

1. Implement `ValidationController` for validating musical structures
2. Implement `UtilityController` for utility functions
3. Enhance AI integration interfaces
4. Implement advanced pattern generation algorithms
5. Add more import/export formats
