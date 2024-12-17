# Note Sequence Generator

A Python-based tool for generating musical note sequences based on scale degrees and chord progressions. This project provides a FastAPI backend for creating and manipulating musical patterns.

Still an ugly baby and not fully working yet.

## Overview

The Note Sequence Generator is a specialized tool that works with scale degrees (1-7) rather than absolute notes (C, D, E, etc.). This approach makes it easier to:

- Work with patterns that can be transposed to any key
- Generate melodies based on chord progressions
- Create reusable melodic and rhythmic templates
- Experiment with different musical styles and progressions

## Features

### Chord Progressions
- Rich library of preset chord progressions including:
  - Jazz standards (II-V-I, Bird Blues, Coltrane Changes)
  - Pop progressions (I-V-vi-IV, Doo-Wop)
  - Modal progressions (So What)
  - Blues variations
  - Rock and EDM patterns
- Custom chord progression creation
- Support for complex chord qualities (maj7, min7, dim, aug)

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

![Type Check](https://github.com/bretbouchard/Note-Gen/actions/workflows/WORKFLOW-FILE/badge.svg


![example workflow](https://github.com/github/docs/actions/workflows/main.yml/badge.svg)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/note-sequence-generator.git
cd note-sequence-generator
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- OpenAPI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

### Example API Calls

```python
# Generate a note sequence from a chord progression
POST /generate/progression
{
    "progression_name": "II-V-I in C Major",
    "pattern_name": "Ascending Scale",
    "rhythm_pattern_name": "Quarter Notes"
}

# Get available chord progressions
GET /presets/progressions

# Generate notes from a single chord
POST /generate/chord
{
    "chord": {
        "root": 1,
        "quality": "major",
        "duration": 4
    }
}
```

## Project Structure

```
note_generator/
├── __init__.py
├── models.py           # Pydantic models
├── note_modulation.py  # Note modulation logic
├── note_sequence.py    # Sequence generation
├── presets.py         # Preset patterns and progressions
└── chord_progressions.py  # Chord progression library

main.py                # FastAPI application
requirements.txt       # Project dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
