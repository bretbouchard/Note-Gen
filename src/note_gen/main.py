"""
FastAPI application setup and configuration.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import threading
from src.note_gen.database.db import MongoDBConnection

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

# Create FastAPI app
app = FastAPI(
    title="Note Generation API",
    description="API for generating musical note sequences",
    version="1.0.0",
    trailing_slash=False
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    if not hasattr(app.state, "db"):
        db_gen = MongoDBConnection(
            uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            db_name=os.getenv("DATABASE_NAME", "note_gen")
        )
        async for db in db_gen:
            app.state.db = db
            break

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    if hasattr(app.state, "db"):
        await app.state.db.client.close()

# Include routers
app.include_router(note_sequence_routes.router, prefix="/api/v1/note-sequences", tags=["note_sequences"])
app.include_router(note_pattern_routes.router, prefix="/api/v1/note-patterns", tags=["note_patterns"])
app.include_router(rhythm_pattern_routes.router, prefix="/api/v1/rhythm-patterns", tags=["rhythm_patterns"])
app.include_router(chord_progression_routes.router, prefix="/api/v1/chord-progressions", tags=["chord_progressions"])
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["users"])
