"""Main router configuration."""
from fastapi import APIRouter
from .sequence_routes import router as sequence_router
from .pattern_routes import router as pattern_router
from .chord_progression_routes import router as chord_progression_router
from .user_routes import router as user_router

router = APIRouter()

# Include all sub-routers with consistent prefixing
router.include_router(
    sequence_router,
    prefix="/api/v1/sequences",
    tags=["sequences"]
)
router.include_router(
    pattern_router,
    prefix="/api/v1/patterns",
    tags=["patterns"]
)
router.include_router(
    chord_progression_router,
    prefix="/api/v1/chord-progressions",
    tags=["chord-progressions"]
)
router.include_router(
    user_router,
    prefix="/api/v1/users",
    tags=["users"]
)
