"""
FastAPI application setup and configuration.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import threading
from src.note_gen.database.db import init_db, close_mongo_connection
from contextlib import asynccontextmanager

from src.note_gen.routers import (
    note_sequence_routes,
    note_pattern_routes,
    rhythm_pattern_routes,
    chord_progression_routes,
    user_routes
)

class ThreadSafeStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stdout)
        self.stream = sys.stdout
        self._lock = threading.Lock()

    def emit(self, record):
        with self._lock:
            try:
                if self.stream and not self.stream.closed:
                    super().emit(record)
            except Exception:
                self.handleError(record)

# Remove all existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure the root logger with our custom handler
handler = ThreadSafeStreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)

# Configure specific loggers
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for managing startup and shutdown processes.
    This replaces the deprecated @app.on_event decorators for startup and shutdown.
    The logic here initializes the database connection when the app starts
    and closes it when the app shuts down.
    """
    await init_db()  # Initialize the database connection
    yield  # This will pause the lifespan until the app is shut down
    await close_mongo_connection()  # Close the database connection

# Create FastAPI app
app = FastAPI(
    title="Note Generation API",
    description="API for generating musical note sequences",
    version="1.0.0",
    lifespan=lifespan,
    trailing_slash=False,
    redirect_slashes=False,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Note Generation API!"}


# Include routers
logger.debug("Registering routers...")
app.include_router(note_sequence_routes.router, prefix="/api/v1/note-sequences", tags=["note-sequences"])
app.include_router(note_pattern_routes.router, prefix="/api/v1/note-patterns", tags=["note-patterns"])
app.include_router(rhythm_pattern_routes.router, prefix="/api/v1/rhythm-patterns", tags=["rhythm-patterns"])
app.include_router(chord_progression_routes.router, prefix="/api/v1/chord-progressions", tags=["chord-progressions"])
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["users"])
logger.debug("All routers registered")


