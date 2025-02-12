"""
Main FastAPI application.
"""
import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from src.note_gen.routers.user_routes import router as user_router
from src.note_gen.routers.chord_progression_routes import router as chord_progression_router
from src.note_gen.routers.note_pattern_routes import router as note_pattern_router
from src.note_gen.routers.rhythm_pattern_routes import router as rhythm_pattern_router, simple_router as rhythm_pattern_simple_router
from src.note_gen.routers.note_sequence_routes import router as note_sequence_router

from src.note_gen.database import init_db, close_mongo_connection, get_db
import logging
import logging.config
import json


# Get the absolute path to the logging_config.json file
config_path = Path(__file__).parent / 'logging_config.json'

# Configure logging (using your logging_config.json)
with open(config_path, 'r') as f:
    config = json.load(f)
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting up FastAPI application...")
    try:
        # Initialize the database connection
        await init_db()
        logger.info("MongoDB connection initialization started")
        db = await get_db().__anext__()
        logger.info("MongoDB connection initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        logger.info("Closing MongoDB connection...")
        await close_mongo_connection()
        logger.info("MongoDB connection closed successfully")
        logger.info("Shutting down FastAPI application...")
        logger.info("Database connection closed successfully")

app = FastAPI(
    title="Note Generator API",
    description="API for generating musical patterns and sequences",
    version="0.1.0",
    redirect_slashes=False,  # Disable trailing slash redirects
    lifespan=lifespan
)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as necessary for your application
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix="/api/v1/users")
app.include_router(chord_progression_router, prefix="/api/v1/chord-progressions")
app.include_router(note_sequence_router, prefix="/api/v1/note-sequences")
app.include_router(rhythm_pattern_router, prefix="/api/v1/rhythm-patterns")
app.include_router(note_pattern_router, prefix="/api/v1/note-patterns")
app.include_router(rhythm_pattern_simple_router, prefix="/api/v1/rhythm-patterns/simple")  # Update prefix

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Note Generation API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    raise HTTPException(status_code=500, detail="An internal server error occurred")