# File: /docs/architecture.md

# Note-Gen Architecture

## System Overview
Note-Gen is a music generation system built with FastAPI and MongoDB, focusing on pattern-based music generation.

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
