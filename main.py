"""
Main FastAPI application.
"""
import os
import json
import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import database and routers
from src.note_gen.database.db import init_db, close_mongo_connection
from src.note_gen.routers.user_routes import router as user_router
from src.note_gen.routers.chord_progression_routes import router as chord_progression_router
from src.note_gen.routers.note_pattern_routes import router as note_pattern_router
from src.note_gen.routers.note_sequence_routes import router as note_sequence_router
from src.note_gen.routers.rhythm_pattern_routes import router as rhythm_pattern_router


from src.note_gen.routers.sequence_generation_routes import router as sequence_generation_routes

# Configure logging
config_path = Path(__file__).parent / 'logging_config.json'
with open(config_path, 'r') as f:
    config = json.load(f)
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.
    Handles database connection initialization and cleanup.
    """
    logger.info("Starting up FastAPI application...")
    try:
        await init_db()
        logger.info("Database initialization successful")
        yield
    except Exception as e:
        logger.error(f"Startup error: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down FastAPI application...")
        await close_mongo_connection()

# Initialize FastAPI application
app = FastAPI(
    title="Note Generator API",
    description="API for generating musical patterns and sequences",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes with versioning
API_V1_PREFIX = "/api/v1"
app.include_router(user_router, prefix=f"{API_V1_PREFIX}/users")
app.include_router(chord_progression_router, prefix=f"{API_V1_PREFIX}/chord-progressions")
app.include_router(note_sequence_router, prefix=f"{API_V1_PREFIX}/note-sequences")
app.include_router(rhythm_pattern_router, prefix=f"{API_V1_PREFIX}/rhythm-patterns")
app.include_router(note_pattern_router, prefix=f"{API_V1_PREFIX}/note-patterns")
app.include_router(sequence_generation_routes, prefix=f"{API_V1_PREFIX}/generate-sequence")



@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to the Note Generation API",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "operational"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    error_msg = str(exc)
    logger.error(f"Unhandled error: {error_msg}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail="An internal server error occurred. Please try again later."
    )