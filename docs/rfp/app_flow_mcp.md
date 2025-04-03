# Note-Gen MCP Server Flow

This document outlines the high-level flow of the Note-Gen MCP (Model-Controller-Presenter) Server for Musical Composition with AI Integration.

## MCP Architecture Overview

The Note-Gen application follows the Model-Controller-Presenter (MCP) architecture pattern:

1. **Models**: Data structures and business logic
   - Pydantic models for data validation
   - Domain models representing musical concepts
   - Data transfer objects (DTOs) for API communication

2. **Controllers**: Business logic and application flow
   - Handle requests from API endpoints
   - Coordinate between models and presenters
   - Implement core musical algorithms and transformations

3. **Presenters**: Data transformation for presentation
   - Convert internal models to API response formats
   - Handle serialization and deserialization
   - Format data for different output types (JSON, MIDI, etc.)

4. **Repositories**: Data access layer
   - MongoDB interactions through Motor
   - CRUD operations for all musical components
   - Query optimization and data retrieval

## Application Flow

### 1. Request Handling
- API request received by FastAPI router
- Request validated using Pydantic models
- Request routed to appropriate controller

### 2. Controller Processing
- Controller receives validated request data
- Business logic applied to the request
- Repository methods called to retrieve or store data
- Musical transformations and algorithms applied

### 3. Data Persistence
- MongoDB repositories handle data storage and retrieval
- Asynchronous operations using Motor
- Data validation before storage

### 4. Response Preparation
- Presenter transforms internal models to API response format
- Response formatted according to requested content type
- Error handling and status codes applied

### 5. AI Integration
- External AI systems can interact through standardized interfaces
- Structured data provided for AI consumption
- Results from AI processing incorporated into the workflow

## Component Interactions

```
[API Request] → [FastAPI Router] → [Pydantic Validation]
    → [Controller] → [Repository] → [MongoDB]
    → [Controller] → [Presenter] → [API Response]
```

## Key Controllers

1. **PatternController**
   - Manages note patterns and rhythm patterns
   - Handles pattern creation, retrieval, and manipulation

2. **ChordProgressionController**
   - Manages chord progressions and harmonic structures
   - Handles progression creation, retrieval, and analysis

3. **SequenceController**
   - Manages musical sequences combining patterns and progressions
   - Handles sequence creation, playback, and manipulation

4. **ImportExportController**
   - Handles import/export of musical components
   - Supports multiple formats (JSON, CSV)

5. **ValidationController**
   - Validates musical structures and relationships
   - Ensures musical coherence and correctness

## Data Flow for Pattern Creation

1. Client sends pattern creation request with pattern data
2. FastAPI validates request using Pydantic models
3. PatternController processes the request
4. Pattern validated for musical correctness
5. PatternRepository stores the pattern in MongoDB
6. Controller returns success response through Presenter

## AI Integration Flow

1. AI system sends request with musical parameters
2. Controller processes request and retrieves relevant patterns/progressions
3. Musical algorithms applied to generate new content
4. Results stored in database if requested
5. Formatted response returned to AI system

## Integration of Musical Algorithms

The musical algorithms from the Schillinger System will be integrated into the MCP architecture as follows:

1. **Rhythm Generation Algorithms**
   - Implemented in the PatternController and specialized utility classes
   - Interference patterns and rhythmic synchronization will be encapsulated in dedicated service classes
   - Results will be stored as RhythmPattern models in the database

2. **Harmony Generation Algorithms**
   - Implemented in the ChordProgressionController
   - Scale mapping, chord generation, and harmonic frameworks will be handled by specialized service classes
   - Results will be stored as ChordProgression models in the database

3. **Melody Generation Algorithms**
   - Implemented in the PatternController and specialized melody services
   - Melodic axis creation and pitch assignment will be handled by dedicated classes
   - Results will be stored as NotePattern models in the database

4. **Geometric Transformations**
   - Implemented in the TransformationController (to be added)
   - Inversion, retrograde, expansion, and contraction operations will be available as transformation services
   - Can be applied to existing patterns and progressions

5. **Harmony-Melody Integration**
   - Implemented in the SequenceController
   - Combines note patterns, rhythm patterns, and chord progressions into coherent musical sequences
   - Results will be stored as Sequence models in the database

6. **Output Generation**
   - Implemented in the ImportExportController
   - Converts internal models to various output formats (MIDI, JSON, etc.)
   - Handles serialization and formatting for different output types

## Next Steps

1. Implement remaining controllers (ValidationController, UtilityController, TransformationController)
2. Implement the musical algorithm services described above
3. Enhance AI integration interfaces
4. Expand import/export capabilities
5. Implement advanced pattern generation algorithms
