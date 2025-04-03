# Note-Gen Architecture Map

## Core Package Structure
```plaintext
note_gen/
├── core/
│   ├── constants.py         # Musical and system constants
│   ├── enums.py            # System-wide enumerations
│   └── sequence_generator.py # Pattern generation logic
├── models/
│   ├── base.py             # Base model classes
│   ├── chord.py            # Chord representation
│   ├── note.py             # Note representation
│   ├── patterns.py         # Pattern models
│   ├── scale_info.py       # Scale information (100% tested)
│   └── data.py            # Data models for patterns
├── validation/
│   ├── base_validation.py  # Base validation classes
│   ├── pattern_pipeline.py # Pattern validation pipeline
│   ├── validation_manager.py # Validation coordination
│   └── constant_validation.py # Constants validation
├── routers/
│   ├── router.py           # Main API router
│   └── sequence_routes.py  # Sequence endpoints
└── main.py                 # FastAPI application entry
```

## Naming Conventions

### Models
- Base classes: `Base{Type}` (e.g., `BaseModel`, `BasePattern`)
- Pattern classes: `{Type}Pattern` (e.g., `NotePattern`, `RhythmPattern`)
- Data classes: `{Type}Data` (e.g., `NotePatternData`)

### Validation
- Validators: `{Type}Validator` (e.g., `PatternValidator`, `ConstantValidator`)
- Results: `ValidationResult`
- Levels: `ValidationLevel` enum

### Generation
- Generators: `{Type}Generator` (e.g., `NoteGenerator`, `RhythmGenerator`)
- Factory methods: `generate_{type}` (e.g., `generate_pattern`)

### Constants and Enums
- Constants: UPPERCASE_WITH_UNDERSCORE
- Enums: PascalCase
- Types: PascalCase

### Database
- Collections: lowercase_with_underscore
- Queries: `get_{entity}`, `create_{entity}`, `update_{entity}`

## Component Dependencies

### Core Dependencies
- Models → Core (constants, enums)
- Validation → Models
- Generation → Models, Validation
- API Routes → Generation, Models

### External Dependencies
- FastAPI (API framework)
- Pydantic (data validation)
- MongoDB (database)
- pytest (testing)

## Testing Structure
```plaintext
tests/
├── conftest.py            # Test configuration
├── unit/
│   ├── models/           # Model tests
│   ├── validation/       # Validation tests
│   └── generation/       # Generator tests
└── integration/
    ├── api/             # API endpoint tests
    └── database/        # Database integration tests
```

## Validation Hierarchy
1. Model-level validation
2. Pattern-specific validation
3. Musical rule validation
4. Cross-component validation

## Generation Pipeline
1. Input validation
2. Pattern generation
3. Musical rule application
4. Validation checks
5. Output formatting

## API Structure
- `/api/v1/patterns/` - Pattern operations
- `/api/v1/sequences/` - Sequence operations
- `/api/v1/validation/` - Validation endpoints

## Database Collections
- chord_progressions
- rhythm_patterns
- note_patterns