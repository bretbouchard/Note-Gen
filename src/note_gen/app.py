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

# Legacy API routers - to be deprecated
# app.include_router(sequence_router, prefix="/api/v1/note-sequences")
# app.include_router(sequence_routes_router, prefix="/api/v1/note-sequences")
# app.include_router(pattern_router, prefix="/api/v1/patterns")
# app.include_router(user_router, prefix="/api/v1/users")
# app.include_router(rhythm_patterns_router, prefix="/api/v1/patterns/rhythm")

# Health check endpoint
@app.get("/health", tags=["Utilities"])
async def health_check():
    return {"status": "ok"}

# Statistics endpoint
@app.get("/stats", tags=["Utilities"])
async def get_statistics():
    """Get statistics about the database."""
    from motor.motor_asyncio import AsyncIOMotorDatabase
    from note_gen.database.db import get_db_conn
    from note_gen.core.enums import ScaleType

    # Get database connection
    db: AsyncIOMotorDatabase = await get_db_conn()

    # Get counts
    chord_progression_count = await db.chord_progressions.count_documents({})
    note_pattern_count = await db.note_patterns.count_documents({})
    rhythm_pattern_count = await db.rhythm_patterns.count_documents({})
    sequence_count = await db.sequences.count_documents({})
    user_count = await db.users.count_documents({})

    # Get detailed pattern information
    note_patterns_by_scale = {}
    for scale_type in ScaleType:
        count = await db.note_patterns.count_documents({"data.scale_type": scale_type.value})
        if count > 0:
            note_patterns_by_scale[scale_type.name] = count

    # Get chord progressions by key
    chord_progressions_by_key = {}
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    for key in keys:
        count = await db.chord_progressions.count_documents({"key": key})
        if count > 0:
            chord_progressions_by_key[key] = count

    # Get rhythm patterns by time signature
    rhythm_patterns_by_time_sig = {}
    time_signatures = [[4, 4], [3, 4], [6, 8], [5, 4], [7, 8]]
    for time_sig in time_signatures:
        count = await db.rhythm_patterns.count_documents({"time_signature": time_sig})
        if count > 0:
            rhythm_patterns_by_time_sig[f"{time_sig[0]}/{time_sig[1]}"] = count

    return {
        "statistics": {
            "chord_progressions": chord_progression_count,
            "note_patterns": note_pattern_count,
            "rhythm_patterns": rhythm_pattern_count,
            "sequences": sequence_count,
            "users": user_count
        },
        "details": {
            "note_patterns_by_scale": note_patterns_by_scale,
            "chord_progressions_by_key": chord_progressions_by_key,
            "rhythm_patterns_by_time_signature": rhythm_patterns_by_time_sig
        }
    }

# Root endpoint
@app.get("/", tags=["Utilities"])
async def root():
    # Option 1: Return API information
    return {
        "app": "Note Generator API",
        "version": "1.0.0",
        "description": "API for musical pattern generation and manipulation",
        "documentation": "/docs",
        "endpoints": [
            "/api/v1/chord-progressions",
            "/api/v1/patterns",
            "/api/v1/sequences",
            "/api/v1/users",
            "/health",
            "/stats",
            "/patterns-list"
        ]
    }

    # Option 2: Redirect to docs (uncomment to use)
    # return RedirectResponse(url="/docs/")

# List all patterns endpoint
@app.get("/patterns-list", tags=["Utilities"])
async def list_all_patterns():
    """List all patterns in the database by name."""
    from motor.motor_asyncio import AsyncIOMotorDatabase
    from note_gen.database.db import get_db_conn

    # Get database connection
    db: AsyncIOMotorDatabase = await get_db_conn()

    # Get all note patterns
    note_patterns_cursor = db.note_patterns.find({}, {"name": 1, "_id": 1})
    note_patterns = await note_patterns_cursor.to_list(length=None)
    note_patterns_list = [{"id": str(p["_id"]), "name": p["name"]} for p in note_patterns if "name" in p]

    # Get all rhythm patterns
    rhythm_patterns_cursor = db.rhythm_patterns.find({}, {"name": 1, "_id": 1})
    rhythm_patterns = await rhythm_patterns_cursor.to_list(length=None)
    rhythm_patterns_list = [{"id": str(p["_id"]), "name": p["name"]} for p in rhythm_patterns if "name" in p]

    # Get all chord progressions
    chord_progressions_cursor = db.chord_progressions.find({}, {"name": 1, "key": 1, "_id": 1})
    chord_progressions = await chord_progressions_cursor.to_list(length=None)
    chord_progressions_list = [
        {"id": str(p["_id"]), "name": p["name"], "key": p.get("key", "Unknown")}
        for p in chord_progressions if "name" in p
    ]

    return {
        "note_patterns": sorted(note_patterns_list, key=lambda x: x["name"]),
        "rhythm_patterns": sorted(rhythm_patterns_list, key=lambda x: x["name"]),
        "chord_progressions": sorted(chord_progressions_list, key=lambda x: x["name"])
    }

# Redirect to docs
@app.get("/docs", include_in_schema=False, tags=["Utilities"])
async def custom_swagger_ui_redirect():
    return RedirectResponse(url="/docs/")
