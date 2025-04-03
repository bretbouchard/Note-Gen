# Note-Gen: Musical Note Sequence Generator

A Python-based tool for generating musical note sequences based on scale degrees and chord progressions. This project provides a FastAPI backend for creating and manipulating musical patterns.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.0+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

### Prerequisites

- Python 3.9 or higher
- MongoDB 4.4 or higher
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/bretbouchard/Note-Gen.git
cd Note-Gen
```

### Step 2: Set Up Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# For development (optional)
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment Variables (Optional)

Create a `.env` file in the project root with the following variables:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=note_gen
```

## Usage

### Starting the Application

#### Step 1: Start MongoDB

Ensure MongoDB is running:

```bash
# Start MongoDB (if not running as a service)
mongod --dbpath=./data/db
```

#### Step 2: Start the FastAPI Server

```bash
# Using the run script (recommended)
./run.sh
```

This script will:

- Activate the virtual environment if needed
- Start the server on port 8000
- Enable hot reloading (the server will automatically restart when code changes)

Alternatively, you can start the server manually:

```bash
PYTHONPATH=src uvicorn note_gen.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 3: Populate the Database (First Time Setup)

In a new terminal, run:

```bash
# Activate the virtual environment
source venv/bin/activate

# Import chord progressions, note patterns, and rhythm patterns
python scripts/import_chord_progressions.py --clear
python scripts/import_note_patterns.py --clear
python scripts/import_rhythm_patterns.py --clear
```

### Stopping the Application

```bash
# Using the stop script
./stop.sh

# Or press Ctrl+C in the terminal where the server is running
```

### API Documentation

Once the server is running, access the API documentation at:

- OpenAPI (Swagger UI): <http://localhost:8000/docs>
- ReDoc (alternative UI): <http://localhost:8000/redoc>

Note: The server runs on port 8000 by default. If you need to change this, edit the `run.sh` script.

### Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/chord-progressions` | List and manage chord progressions |
| `/api/v1/patterns/note-patterns` | List and manage note patterns |
| `/api/v1/patterns/rhythm-patterns` | List and manage rhythm patterns |
| `/api/v1/sequences` | Create and manage sequences |
| `/stats` | View database statistics |
| `/patterns-list` | View all available patterns |

### Example API Calls

#### Generate a Note Sequence

```http
POST /api/v1/sequences/generate
Content-Type: application/json

{
    "progression_name": "II-V-I in C Major",
    "pattern_name": "Ascending Scale",
    "rhythm_pattern_name": "Basic 4/4"
}
```

#### Get All Chord Progressions

```http
GET /api/v1/chord-progressions
```

#### Get a Specific Note Pattern

```http
GET /api/v1/patterns/note-patterns/{pattern_id}
```

## Development

### Running Tests

```bash
# Activate the virtual environment
source venv/bin/activate

# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=note_gen --cov-report=term-missing

# Run specific test file
python -m pytest tests/path/to/test_file.py
```

### Code Quality Tools

```bash
# Type checking with mypy
mypy src

# Linting with flake8
flake8 src

# Linting with ruff (faster alternative)
ruff check src

# Formatting with black
black src
```

### Debugging

To enable debug logging, set the `DEBUG` environment variable:

```bash
DEBUG=1 ./run.sh
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
