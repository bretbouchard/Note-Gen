"""Main router configuration."""
from fastapi import APIRouter
from .sequence_routes import router as sequence_router
from .pattern_routes import router as pattern_router
from .chord_progression_routes import router as chord_progression_router
from .user_routes import router as user_router

# Create main API router with version prefix
main_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
main_router.include_router(
    sequence_router,
    prefix="/sequences",
    tags=["sequences"]
)

main_router.include_router(
    pattern_router,
    prefix="/patterns",
    tags=["patterns"]
)

main_router.include_router(
    chord_progression_router,
    prefix="/chord-progressions",
    tags=["chord-progressions"]
)

main_router.include_router(
    user_router,
    prefix="/users",
    tags=["users"]
)

# Export the configured router
router = main_router
