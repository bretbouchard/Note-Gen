from fastapi import FastAPI
from .routers.chord_progression_routes import router as chord_progression_router
from .routers.rhythm_pattern_routes import router as rhythm_pattern_router
from .routers.note_pattern_routes import router as note_pattern_router
from .routers.note_sequence_routes import router as note_sequence_router
from .routers.user_routes import router as user_router
from .fetch_patterns import (
    extract_patterns_from_chord_progressions,
    fetch_note_patterns,
    fetch_note_pattern_by_id
)
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

app.include_router(
    chord_progression_router,
    prefix="/api/v1/chord-progressions"
)

# Add rhythm pattern routes
app.include_router(
    rhythm_pattern_router,
    prefix="/api/v1/rhythm-patterns"
)

# Add note pattern routes
app.include_router(
    note_pattern_router,
    prefix="/api/v1/note-patterns"
)

# Add note sequence routes
app.include_router(
    note_sequence_router,
    prefix="/api/v1/note-sequences"
)

# Add user routes
app.include_router(
    user_router,
    prefix="/api/v1/users"
)