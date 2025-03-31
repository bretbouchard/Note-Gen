# Note Sequence Generator

A Python-based tool for generating musical note sequences based on scale degrees and chord progressions. This project provides a FastAPI backend for creating and manipulating musical patterns.

Still an ugly baby and not fully working yet.

## Overview

The Note Sequence Generator is a specialized tool that works with scale degrees (1-7) rather than absolute notes (C, D, E, etc.). This approach makes it easier to:

- Work with patterns that can be transposed to any key
- Generate melodies based on chord progressions
- Create reusable melodic and rhythmic templates
- Experiment with different musical styles and progressions

## Project Structure

```plaintext
note_generator/
├── __init__.py
├── models/
│   ├── chord.py
│   ├── chord_progression.py
│   ├── chord_progression_generator.py
│   ├── chord_roman_utils.py
│   ├── enums.py
│   ├── note.py
│   ├── note_sequence.py
│   └── scale_info.py
├── note_modulation.py  # Note modulation logic
├── note_sequence.py    # Sequence generation
├── presets.py         # Preset patterns and progressions
└── chord_progressions.py  # Chord progression library

main.py                # FastAPI application
requirements.txt       # Project dependencies
```

## Features

### Chord Progressions

- Rich library of preset chord progressions including:
  - Jazz standards (II-V-I, Bird Blues, Coltrane Changes)
  - Pop progressions (I-V-vi-IV, Doo-Wop)
  - Modal progressions (So What)
  - Blues variations
  - Rock and EDM patterns
- Custom chord progression creation
- Random progression generation
- Support for complex chord qualities (maj7, min7, dim, aug)
- Robust error handling for invalid scale degrees and chord notes

### Note Generation

- Scale-degree based note generation
- Chord-aware note modulation
- Pattern-based sequence generation
- Support for various musical styles

### API Endpoints

- Generate notes from chord progressions
- Generate notes from individual chords
- Access preset chord progressions
- Access note and rhythm patterns

## Technical Stack

- **Backend Framework:** FastAPI
- **Data Validation:** Pydantic
- **Server:** Uvicorn
- **Language:** Python 3.8+
- **Testing:** Pytest
- **Logging:** Python's built-in logging module

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/note-sequence-generator.git
cd note-sequence-generator
```

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Start the FastAPI server:

```bash
uvicorn main:app --reload

PYTHONPATH=src uvicorn main:app --reload

PYTHONPATH=src uvicorn note_gen.main:app --reload

```

Start the MongoDB database:

```bash
mongosh
use note_gen
```

mongo mongodb://localhost:27017/note_gen

Tests:

```bash
PYTHONPATH=/Users/bretbouchard/apps/Note-Gen/backend python -m pytest . -s -v
```

Access the API documentation:

- OpenAPI documentation: <http://localhost:8000/docs>
- ReDoc documentation: <http://localhost:8000/redoc>

### Example API Calls

Generate a note sequence from a chord progression

```python
POST /generate/progression
{
    "progression_name": "II-V-I in C Major",
    "pattern_name": "Ascending Scale",
    "rhythm_pattern_name": "Quarter Notes"
}
```

Get available chord progressions

```python
GET /presets/progressions
```

Generate notes from a single chord

```python
POST /generate/chord
{
    "chord": {
        "root": 1,
        "quality": "MAJOR",
        "duration": 4
    }
}
```

Generate a random chord progression

```python
POST /generate/progression/random
{
    "length": 4,
    "scale": "C MAJOR"
}
```

## Testing

pytest
mypy src
black --check src


## Contest Priming
Read README.md, .windsurfrules, and run git ls-files to understand the codebase

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For MAJOR changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)



@src/note_gen/models/note.py @src/note_gen/models/chord.py @src/note_gen/models/scale.py @src/note_gen/models/scale_info.py @src/note_gen/models/fake_scale_info.py @src/note_gen/models/patterns.py @models/rhythm.py @src/note_gen/core/constants.py @src/note_gen/core/enums.py @src/note_gen/validation/validation_manager.py @src/note_gen/schemas/validation_response.py 