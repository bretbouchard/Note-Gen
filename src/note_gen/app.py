"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
# Import MCP architecture routers
from .routers.chord_progressions import router as chord_progressions_router
from .routers.patterns import router as patterns_router
from .routers.sequences import router as sequences_router
from .routers.users import router as users_router
from .routers.validation import router as validation_router
from .routers.import_export import router as import_export_router
from .routers.utility import router as utility_router

# Legacy API routers - to be deprecated
# from .api.sequence_api import router as sequence_router
# from .api.pattern_api import router as pattern_router
# from .api.user_api import router as user_router
# from .api.routes.rhythm_patterns import router as rhythm_patterns_router
# from .routers.sequence_routes import router as sequence_routes_router
from .database.db import init_db, close_mongo_connection

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Handle startup and shutdown events."""
    await init_db()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Note Generator API",
    description="API for musical pattern generation and manipulation",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add exception handler for rate limit errors
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(*_):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded: 60 per 1 minute"}
    )

# Include MCP architecture routers with proper prefixes
app.include_router(chord_progressions_router, prefix="/api/v1/chord-progressions")
app.include_router(patterns_router, prefix="/api/v1/patterns")
app.include_router(sequences_router, prefix="/api/v1/sequences")
app.include_router(users_router, prefix="/api/v1/users")
app.include_router(validation_router, prefix="/api/v1/validation")
app.include_router(import_export_router, prefix="/api/v1/import-export")
app.include_router(utility_router)

# Legacy API routers - to be deprecated
# app.include_router(sequence_router, prefix="/api/v1/note-sequences")
# app.include_router(sequence_routes_router, prefix="/api/v1/note-sequences")
# app.include_router(pattern_router, prefix="/api/v1/patterns")
# app.include_router(user_router, prefix="/api/v1/users")
# app.include_router(rhythm_patterns_router, prefix="/api/v1/patterns/rhythm")

# Legacy endpoints have been moved to the utility controller

# Root endpoint has been moved to the utility controller

# Patterns list endpoint has been moved to the utility controller

# Redirect to docs
@app.get("/docs", include_in_schema=False, tags=["Utilities"])
async def custom_swagger_ui_redirect():
    return RedirectResponse(url="/docs/")
