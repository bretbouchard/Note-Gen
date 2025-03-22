"""Main router configuration."""
from fastapi import APIRouter
from .note_pattern_routes import router as note_pattern_router
from .rhythm_pattern_routes import router as rhythm_pattern_router
from .chord_progression_routes import router as chord_progression_router
from .note_sequence_routes import router as note_sequence_router
from .pattern_routes import router as pattern_router

router = APIRouter()

# Include all sub-routers
router.include_router(note_pattern_router, prefix="/api/v1/note-patterns", tags=["note-patterns"])
router.include_router(rhythm_pattern_router, prefix="/api/v1/rhythm-patterns", tags=["rhythm-patterns"])
router.include_router(chord_progression_router, prefix="/api/v1/chord-progressions", tags=["chord-progressions"])
router.include_router(note_sequence_router, prefix="/api/v1/note-sequences", tags=["note-sequences"])
router.include_router(pattern_router, prefix="/api/v1/patterns", tags=["patterns"])