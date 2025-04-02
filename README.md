# Note-Gen: Musical Note Sequence Generator

A Python-based tool for generating musical note sequences based on scale degrees and chord progressions. This project provides a FastAPI backend for creating and manipulating musical patterns.

## Overview

The Note-Gen is a specialized tool that works with scale degrees (1-7) rather than absolute notes (C, D, E, etc.). This approach makes it easier to:

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
- **Database:** MongoDB
- **Data Validation:** Pydantic
- **Server:** Uvicorn
- **Language:** Python 3.8+
- **Testing:** Pytest
- **Type Checking:** Mypy
- **Linting:** Flake8, Ruff
- **Logging:** Python's built-in logging module

## Project Structure

```plaintext
note-gen/
├── src/                    # Source code
│   └── note_gen/           # Main package
│       ├── api/            # API endpoints and middleware
│       ├── core/           # Core functionality and constants
│       ├── database/       # Database connections and repositories
│       ├── dependencies/   # FastAPI dependencies
│       ├── factories/      # Factory classes for creating objects
│       ├── generators/     # Generators for musical elements
│       ├── models/         # Data models
│       ├── routers/        # API routers
│       ├── schemas/        # Pydantic schemas
│       ├── services/       # Business logic services
│       ├── typings/        # Type definitions
│       └── validation/     # Validation logic
├── tests/                  # Test suite
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── tools/                  # Development tools
```

## Installation

Clone the repository:

```bash
git clone https://github.com/bretbouchard/Note-Gen.git
cd Note-Gen
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## Usage

### Starting the Application

Start the MongoDB database:

```bash
# Start MongoDB (if not running as a service)
mongod --dbpath=./data/db
```

Start the FastAPI server:

```bash
# Using the PYTHONPATH to ensure imports work correctly
PYTHONPATH=src uvicorn note_gen.main:app --reload
```

### API Documentation

Access the API documentation:

- OpenAPI documentation: <http://localhost:8000/docs>
- ReDoc documentation: <http://localhost:8000/redoc>

### Example API Calls

Generate a note sequence from a chord progression:

```http
POST /api/v1/sequences/generate
{
    "progression_name": "II-V-I in C Major",
    "pattern_name": "Ascending Scale",
    "rhythm_pattern_name": "Quarter Notes"
}
```

Get available chord progressions:

```http
GET /api/v1/chord-progressions
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src.note_gen

# Type checking
mypy src
```

### Code Quality

```bash
# Linting
flake8 src
ruff check src

# Formatting
black src
```

## Documentation

Additional documentation is available in the `docs/` directory:

- [Architecture Overview](docs/architecture.md)
- [Technical Documentation](docs/technical.md)
- [Product Requirements](docs/product_requirement_docs.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)
