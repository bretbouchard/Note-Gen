import os
import sys
import logging
import threading
from contextlib import asynccontextmanager
from src.note_gen.database.db import init_db, close_mongo_connection
from src.note_gen import app as note_gen_app
from fastapi.middleware.cors import CORSMiddleware

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
async def lifespan(app):
    await init_db()
    yield
    await close_mongo_connection()

# Update the imported app with needed middleware and lifespan
app = note_gen_app
app.lifespan = lifespan

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Note Generation API!"}

# The routers are already included in the note_gen_app import
logger.info("Note Generation API is initialized and ready")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)