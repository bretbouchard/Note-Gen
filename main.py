import os
import sys
import logging
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.note_gen.database.db import init_db, close_mongo_connection
from src.note_gen.routers import (
    note_sequence_routes,
    note_pattern_routes,
    rhythm_pattern_routes,
    chord_progression_routes,
    user_routes,
)

# Set up a thread-safe logging handler
class ThreadSafeStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stdout)
        self._lock = threading.Lock()

    def emit(self, record):
        with self._lock:
            try:
                if self.stream and not self.stream.closed:
                    super().emit(record)
            except Exception:
                self.handleError(record)

# Remove existing handlers and configure logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
handler = ThreadSafeStreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_mongo_connection()

# Create FastAPI app with API metadata and custom behavior
app = FastAPI(
    title="Note Generation API",
    description="API for generating musical note sequences",
    version="1.0.0",
    lifespan=lifespan,
    trailing_slash=False,
    redirect_slashes=False,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Note Generation API!"}

# Include routers with specific prefixes and tags
logger.debug("Registering routers...")
app.include_router(note_sequence_routes.router, prefix="/api/v1/note-sequences", tags=["note-sequences"])
app.include_router(note_pattern_routes.router, prefix="/api/v1/note-patterns", tags=["note-patterns"])
app.include_router(rhythm_pattern_routes.router, prefix="/api/v1/rhythm-patterns", tags=["rhythm-patterns"])
app.include_router(chord_progression_routes.router, prefix="/api/v1/chord-progressions", tags=["chord-progressions"])
app.include_router(user_routes.router, prefix="/api/v1/users", tags=["users"])
logger.debug("All routers registered")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)