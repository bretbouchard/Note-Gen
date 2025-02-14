# Current Task: Fix MongoDB Connection Issues in Tests

## Problem
Tests are failing due to:
1. Missing `MongoDBConnection` class that was previously used but has been replaced with direct `AsyncIOMotorClient` usage
2. `get_db_conn()` not supporting async context manager protocol
3. Improper database cleanup between tests

## Plan
[X] Review and update database connection code in test files
[X] Update test files to use new async MongoDB connection pattern
[X] Ensure proper test database setup and teardown
[X] Create AsyncDBConnection class to support async context manager protocol
[X] Update AsyncDBConnection to use sync context manager instead
[X] Update test files to use new connection pattern
[ ] Verify test isolation and cleanup

## Files Updated
1. src/note_gen/database/db.py
   - Created AsyncDBConnection class to support sync context manager protocol
   - Updated get_db_conn to return AsyncDBConnection instance
   - Added proper connection cleanup in __exit__
   - Fixed global client handling in __exit__
2. tests/api/test_fetch_patterns.py
   - Updated test_db fixture to use AsyncDBConnection
   - Fixed database connection pattern
3. tests/api/test_user_routes.py
   - Updated test_db fixture to use AsyncDBConnection
   - Simplified database setup/teardown
4. tests/models/test_scale.py
   - Updated all test functions to use sync context manager
   - Fixed test assertions to match new database pattern
   - Removed async context manager usage

## Progress
1. Fixed the `MongoDBConnection` import issues
2. Fixed the database connection pattern in test fixtures
3. Added proper sync context manager support
4. Updated test files to use new connection pattern
5. Fixed global client handling in cleanup

## Next Steps
1. Update remaining test files to use AsyncDBConnection
2. Run the tests to verify the changes
3. Check for any remaining issues with database setup/teardown
4. Add any necessary error handling for database operations

## Lessons Learned
- When updating database connection patterns, ensure all test fixtures are updated to match the new pattern
- Use environment variables for database configuration in tests
- Prefer direct client usage over custom connection classes for better maintainability
- Always ensure proper database cleanup between tests to maintain isolation
- Use sync context managers for simpler resource cleanup in test code
- Handle global state carefully in connection managers to avoid leaks

## Development Best Practices

### General
- For website image paths, always use the correct relative path (e.g., 'images/filename.png') and ensure the images directory exists
- Add debug information to stderr while keeping the main output clean in stdout for better pipeline integration
- When using seaborn styles in matplotlib, use 'seaborn-v0_8' instead of 'seaborn' as the style name due to recent seaborn version changes

### MongoDB and FastAPI Integration
- Always add trailing slashes to FastAPI endpoints to prevent 307 redirects
- Use consistent URL patterns across all routes
- Handle both sync and async operations appropriately
- Use AsyncIOMotorDatabase for async MongoDB operations
- Use fixtures for database setup and teardown
- Clean up collections between tests to prevent interference
- Use `{"is_deleted": {"$ne": True}}` to filter out soft-deleted records
- Convert potential ObjectId strings safely
- Handle pymongo-specific errors separately from general exceptions

### Testing and Validation
- Match error messages in test assertions for specific validation errors
- Include all required parameters in test data (e.g., duration and velocity for Note objects)
- Use proper async test fixtures with clear setup and teardown
- Focus on improving core functionality coverage before utility modules
- Use specific error types for different validation failures
- Include helpful error messages that match test expectations
- Handle both sync and async validation appropriately
- Log validation failures with context for debugging

### Pydantic and Data Validation
- In Pydantic v2 field validators:
  - Use a two-step validation process: first check the pattern, then validate values
  - Ensure error messages are specific and match test expectations
  - Handle type conversions and additional checks in validation methods
- When working with test frameworks, use appropriate test doubles:
  - `FakeScaleInfo` for mimicking `ScaleInfo` in tests
  - Allow multiple similar types that share core functionality
  - Use `isinstance()` with multiple types for interface compatibility

## Music-Specific Lessons

### Note and Scale Handling
- Always normalize note names to uppercase
- Handle special cases like 'EB' → 'Eb'
- Use strict regex validation for note names
- Ensure MIDI numbers are within 0-127 range
- Handle flat notes correctly (e.g., 'Bb' → 'A#')
- Support multiple note initialization methods
- When designing enums for musical contexts:
  - Provide robust string conversion methods with aliases
  - Implement comprehensive validation for input formats
  - Use case-insensitive normalization for input parsing
  - Add logging to track conversion processes

### Pattern Generation
- Make `index` field optional in `NotePatternData` model
- Generate random index when missing
- Provide sensible defaults for optional fields
- Use type hints and validators
- Log warnings for missing optional fields
- Validate pattern intervals within -12 to 12 semitones
- Ensure note patterns have at least one note
- Validate time signature format and values
- Check for overlapping notes in rhythm patterns
- Handle swing ratio ranges (0.5-0.75)
- Support different groove types (straight, swing, shuffle)

### Chord Progression Management
- Use `model_dump()` instead of `dict()` for better serialization
- Handle complex type conversions explicitly
- Implement granular error handling
- Log validation errors without breaking operations
- Validate:
  - Required fields
  - Chord progression structure
  - Duplicate progression names
  - Key and scale type validity

### Logging Best Practices
- Log at different severity levels (info, warning, error)
- Include context in log messages (e.g., pattern_id)
- Log full traceback for unexpected errors
- Provide descriptive error details in HTTP responses
- Add detailed logging for CRUD operations
- Include context-specific log messages
- Log validation errors and database interactions
