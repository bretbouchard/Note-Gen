"""Router initialization."""
from .patterns import router as patterns_router
from .sequences import router as sequences_router
from .chord_progressions import router as chord_progressions_router
from .users import router as users_router
from .generate import router as generate_router

__all__ = [
    "patterns_router",
    "sequences_router",
    "chord_progressions_router",
    "users_router",
    "generate_router",
]
