# Note-Gen Architecture

## System Overview
Note-Gen is a music generation system built with FastAPI and MongoDB, focusing on pattern-based music generation. The application follows the Model-Controller-Presenter (MCP) architecture, which provides a clean separation of concerns and makes the codebase more maintainable and testable.

## MCP Architecture Overview

The Note-Gen application follows the Model-Controller-Presenter (MCP) architecture, which is a variation of the traditional Model-View-Controller (MVC) pattern. This architecture provides a clean separation of concerns and makes the codebase more maintainable and testable.

### Components

#### Models

Models represent the data structures and business logic of the application. They are responsible for:
- Defining the structure of the data
- Validating data
- Providing methods for data manipulation

Examples:
- `ChordProgression`
- `NotePattern`
- `RhythmPattern`
- `Sequence`
- `User`

#### Controllers

Controllers handle the business logic of the application. They are responsible for:
- Processing requests from the routers
- Interacting with repositories to access data
- Implementing business rules
- Coordinating between different components

Examples:
- `ChordProgressionController`
- `PatternController`
- `SequenceController`
- `UserController`

#### Presenters

Presenters format data for presentation to the client. They are responsible for:
- Transforming model data into a format suitable for API responses
- Handling presentation-specific logic
- Ensuring a clean separation between business logic and presentation

Examples:
- `ChordProgressionPresenter`
- `PatternPresenter`
- `SequencePresenter`
- `UserPresenter`

#### Routers

Routers define the API endpoints and handle HTTP requests. They are responsible for:
- Defining routes and HTTP methods
- Validating request data
- Calling the appropriate controller methods
- Returning responses to the client

Examples:
- `chord_progressions.py`
- `patterns.py`
- `sequences.py`
- `users.py`

#### Repositories

Repositories provide an abstraction layer for data access. They are responsible for:
- Interacting with the database
- Providing CRUD operations for models
- Handling database-specific logic

Examples:
- `BaseRepository`
- `MongoDBRepository`

### Flow of Control

1. A client sends an HTTP request to the API
2. The router receives the request and validates the input
3. The router calls the appropriate controller method
4. The controller processes the request, interacting with repositories as needed
5. The controller returns the result to the router
6. The router uses the presenter to format the result for the client
7. The formatted result is returned to the client as an HTTP response

## Core Components

### 1. Data Models
- Note
  - Enhanced validation framework
  - Complex transformation support
  - Octave and duration handling
- ChordProgression
  - Roman numeral integration
  - Voice leading rules
  - Scale-aware progression generation
- ScaleInfo (100% tested)
  - Comprehensive validation
  - Scale degree calculations
  - Chord quality mappings
- Pattern (Note and Rhythm)
  - Consolidated validation framework
  - Groove pattern support
  - Compound time signatures

### 2. API Layer
- FastAPI backend
- Standardized response format
- Error handling middleware
- Rate limiting
- Validation integration
- Response standardization

### 3. Database Layer
- MongoDB with repository pattern
- Connection pooling
- Transaction support
- Data validation
- Migration system
- Error handling and retries
- Standardized connection management

### 4. Music Generation Engine
- Pattern-based generation
- Scale-aware note generation
- Rhythm pattern interpretation
- Voice leading validation
- Chord compatibility checks

### 5. Validation Framework
- ValidationManager
- Multi-level validation support
- Result tracking system
- Musical rule validation
- Pattern-specific validation

## Component Relationships
- Pattern generation relies on Scale information
- Chord progressions build on Scale and Note models
- API layer uses repositories for data access
- Validation occurs at Model, API, and Database levels
- ValidationManager coordinates cross-component validation

## Technical Decisions
- Pydantic v2 for validation
- FastAPI for API framework
- MongoDB for flexible pattern storage
- Repository pattern for data access
- Comprehensive test coverage approach
- Modular validation framework
- MCP architecture for clean separation of concerns

## Benefits of MCP Architecture

- **Separation of Concerns**: Each component has a specific responsibility, making the code more maintainable
- **Testability**: Components can be tested in isolation, making it easier to write unit tests
- **Flexibility**: Components can be replaced or modified without affecting other parts of the system
- **Scalability**: The architecture can scale to handle more complex requirements
- **Reusability**: Components can be reused across different parts of the application

## Directory Structure

```plaintext
note-gen/
├── src/
│   └── note_gen/
│       ├── controllers/       # Business logic controllers
│       ├── models/            # Data models
│       ├── presenters/        # Data formatting for presentation
│       ├── routers/           # API endpoints
│       ├── database/          # Database connections and repositories
│       ├── dependencies/      # FastAPI dependencies
│       └── ...
├── tests/
│   ├── controllers/           # Tests for controllers
│   ├── models/                # Tests for models
│   ├── presenters/            # Tests for presenters
│   ├── routers/               # Tests for routers
│   └── ...
└── ...
```

## API Structure

The API is structured around resources, with each resource having its own router, controller, and presenter:

- `/api/v1/chord-progressions`: Endpoints for chord progression operations
- `/api/v1/patterns`: Endpoints for pattern operations
- `/api/v1/sequences`: Endpoints for sequence operations
- `/api/v1/users`: Endpoints for user operations

Each endpoint follows RESTful principles, using appropriate HTTP methods for different operations:
- `GET`: Retrieve resources
- `POST`: Create resources
- `PUT`: Update resources
- `DELETE`: Delete resources
