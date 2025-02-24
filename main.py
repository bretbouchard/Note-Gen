from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.note_gen.routers import (
    chord_progression_routes,
    note_pattern_routes,
    note_sequence_routes,
    rhythm_pattern_routes,
    user_routes,
)
from src.note_gen.database.db import init_db
from contextlib import asynccontextmanager
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan, openapi_prefix="/api/v1")

# CORS setup - Allow requests from your frontend(s)
origins = [
    "http://localhost",  # Example: Allow local development
    "http://localhost:3000",  # Example: Allow React app
    "http://localhost:8000", #Allow swagger doc
    "*",  # Only for development, REMOVE IN PRODUCTION!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - ONCE EACH
app.include_router(note_sequence_routes.router)
app.include_router(note_pattern_routes.router)
app.include_router(rhythm_pattern_routes.router)
app.include_router(chord_progression_routes.router)
app.include_router(user_routes.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)