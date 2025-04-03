# Project Memories

## Validation and Testing

### Test Coverage
Current priority tasks (ordered by coverage):
- note.py (31% coverage)
  - Note validation methods
  - Octave handling
  - Duration calculations
  - Missing: 260 lines including validation logic and note transformations
  - Added: Enhanced validation framework integration
- chord_progression_generator.py (50% coverage)
  - Progression generation logic
  - Chord validation
  - Scale integration
  - Added: Roman numeral integration
  - Added: Enhanced validation support
- scale_info.py (100% coverage)
  - Validation methods
  - Scale degree calculations
  - Chord quality mappings
  - Added: Complete test coverage
  - Added: Edge case handling

### Database Layer Implementation
- Using MongoDB with repository pattern
- Implemented connection pooling
- Added standardized connection management
- Created migration system
- Added transaction support
- Using proper error handling and retries

### NotePattern Structure
- Consolidated implementation in src/note_gen/models/patterns.py
- Enhanced validation for both string and dictionary formats
- Added comprehensive pattern validation
- Implemented voice leading validation
- Added rhythm pattern support with groove features

### Pydantic Usage
- Using Pydantic V2 style @field_validator decorators
- Using 'cls' as first argument in validator methods
- Using Field() function with Annotated for type hints
- Added model_validator for complex validations
- Implementing proper ValidationError handling

### Validation Framework
- Implemented ValidationManager
- Added support for validation levels
- Created comprehensive validation result tracking
- Added pattern-specific validation rules
- Implemented musical rule validation

### Testing Strategy
- Using proper test fixtures
- Implementing comprehensive coverage tracking
- Following TDD for new features
- Using parameterized tests for edge cases
- Maintaining coverage documentation

## Technical Details
- API improvements needed:
  - API versioning support
  - OpenAPI documentation
  - Authentication/authorization
- Constants and enum validation
- Voice leading rule validation
- Range validation

## Code Structure
- Properly organized imports
- Consistent validation patterns
- Clear error handling
- Comprehensive test coverage

## Next Steps (Prioritized)
1. Complete test coverage improvements for core modules
2. Implement remaining validation features
3. Complete database transaction support
4. Enhance documentation coverage
5. Standardize MongoDB connections across scripts
