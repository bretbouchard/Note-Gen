"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from .api.sequence_api import router as sequence_router
from .api.pattern_api import router as pattern_router
from .api.user_api import router as user_router
from .api.routes.rhythm_patterns import router as rhythm_patterns_router
from .database.db import init_db, close_mongo_connection

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

@asynccontextmanager
async def lifespan(app: FastAPI):
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
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded: 60 per 1 minute"}
    )

# Include all routers with proper prefixes
app.include_router(sequence_router, prefix="/api/v1/note-sequences")
app.include_router(pattern_router, prefix="/api/v1/patterns")
app.include_router(user_router, prefix="/api/v1/users")
app.include_router(rhythm_patterns_router, prefix="/api/v1/patterns/rhythm")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
