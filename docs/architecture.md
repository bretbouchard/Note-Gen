# File: /docs/architecture.md

# Note-Gen Architecture

## System Overview
Note-Gen is a music generation system built with FastAPI and MongoDB, focusing on pattern-based music generation.

## Core Components

### 1. Data Models
- Note
- ChordProgression
- ScaleInfo
- Pattern (Note and Rhythm)

### 2. API Layer
- FastAPI backend
- Standardized response format
- Error handling middleware
- Rate limiting

### 3. Database Layer
- MongoDB with repository pattern
- Connection pooling
- Transaction support
- Data validation

### 4. Music Generation Engine
- Pattern-based generation
- Scale-aware note generation
- Rhythm pattern interpretation

## Component Relationships
- Pattern generation relies on Scale information
- Chord progressions build on Scale and Note models
- API layer uses repositories for data access
- Validation occurs at both API and Model levels

## Technical Decisions
- Pydantic v2 for validation
- FastAPI for API framework
- MongoDB for flexible pattern storage
- Repository pattern for data access