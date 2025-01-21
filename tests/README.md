# Test Suite for Note-Gen

This directory contains the test suite for the Note-Gen application. The tests are organized into subdirectories based on functionality, primarily focusing on API endpoints and models.

## Directory Structure

- **api/**: Contains tests related to the API endpoints.
  - **test_api.py**: General API tests.
  - **test_chord_progression_check.py**: Tests for chord progression functionality.
  - **test_generate_sequence.py**: Tests for sequence generation functionality.
  - **test_note_pattern_check.py**: Tests for note pattern functionality.
  - **test_note_sequence.py**: Tests for note sequence functionality.
  - **test_rhythm_pattern_check.py**: Tests for rhythm pattern functionality.
  - **test_user_routes.py**: Tests for user-related routes.

- **models/**: Contains tests related to the application models.
  - **test_Integration.py**: Integration tests.
  - **test_chord.py**: Tests for chord functionality.
  - **test_chord_progression.py**: Tests for chord progression functionality.
  - **test_chord_progression_generator.py**: Tests for chord progression generator functionality.
  - **test_chord_quality.py**: Tests for chord quality functionality.
  - **test_fetch_import_patterns.py**: Tests for fetching import patterns functionality.
  - **test_note.py**: Tests for note functionality.
  - **test_note_event.py**: Tests for note events.
  - **test_note_pattern.py**: Tests for note pattern functionality.
  - **test_note_sequence_generator.py**: Tests for note sequence generator functionality.
  - **test_pattern_type.py**: Tests for pattern types.
  - **test_patterns.py**: Tests for patterns.
  - **test_presets.py**: Tests for presets functionality.
  - **test_rhythm_note.py**: Tests for rhythm notes.
  - **test_rhythm_pattern.py**: Tests for rhythm patterns.
  - **test_roman.py**: Tests for Roman numerals.
  - **test_scale.py**: Tests for scales.
  - **test_scale_degree.py**: Tests for scale degrees.
  - **test_sequence_and_rhythm.py**: Tests for sequence and rhythm functionality.

## Running Tests

To run the tests, use the following command:

```bash
pytest
```

Make sure you have the required dependencies installed and your test database set up before running the tests.

## Logging

Logs for test runs can be found in the `logs/` directory. Please review these logs for any issues that may arise during testing.

## Contribution

If you wish to contribute to the tests, ensure that you follow the naming conventions and directory structure outlined above to maintain consistency.
