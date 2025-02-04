from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException           
from pydantic import BaseModel  
from typing import List, Optional
from src.note_gen.routers.user_routes import router as user_router
from src.note_gen.routers.chord_progression_routes import router as chord_progression_router
from src.note_gen.import_presets import initialize_client, run_imports
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import tracemalloc
from dotenv import load_dotenv
import os
import uvicorn
import json
import os

load_dotenv()  # Load environment variables from .env file

# Get the absolute path to the logs directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

import logging
import logging.config

# Load logging config
with open('logging_config.json', 'r') as f:
    config = json.load(f)
logging.config.dictConfig(config)

# Set up the logger
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = 'mongodb://localhost:27017/'
client: AsyncIOMotorClient = AsyncIOMotorClient(DATABASE_URL)
tracemalloc.start()

# ... rest of your code remains the same ...

class DBConnection:
    def __init__(self, client: AsyncIOMotorClient) -> None:
        self.client = client

    async def __aenter__(self):
        return self.client.note_gen  # Use your database name here

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.client.close()  # Close the client when done

async def get_db() -> AsyncIOMotorDatabase:
    db = client.note_gen  # Use your database name here
    return db  # Return the database connection directly

class ScaleDegree(BaseModel):
    degree: int
    note: str
 
class ChordProgressionRequest(BaseModel):
    style: str = "basic"
    start_degree: Optional[int] = None

class ScaleInfo(BaseModel):
    root: str
    scale: str

class ChordProgressionGenerator(BaseModel):
    """Generator for chord progressions."""
    progression: List[ScaleDegree] = []  # Default to an empty list
    scale_info: ScaleInfo

    def generate_progression(self, style: str = "basic", start_degree: Optional[int] = None) -> List[ScaleDegree]:
        """Generate a chord progression."""
        # This is a placeholder implementation
        return self.progression

    def parse_progression(self, progression_str: str) -> List[str]:
        """Parse a chord progression string."""
        # This is a placeholder implementation
        return progression_str.split()

    def generate_notes_from_chord(self, progression: List[str]) -> List[str]:
        """Generate notes from a chord progression."""
        # This is a placeholder implementation
        return progression

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info('FastAPI application starting...')
        await run_imports()
        logger.info("Application started...")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
    yield
    logger.info("Shutting down the application...")

app = FastAPI(lifespan=lifespan)


app.include_router(user_router, prefix="", tags=["User Routes"])
app.include_router(chord_progression_router, prefix="/api", tags=["Chord Progression Routes"])

# Initialize your generators
root_note = 'C'  # Example root note
scale = 'MAJOR'  # Example scale type
scale_info = ScaleInfo(root=root_note, scale=scale)
chord_generator = ChordProgressionGenerator(scale_info=scale_info)

@app.post("/generate_progression/")
async def generate_progression(request: ChordProgressionRequest) -> List[ScaleDegree]:
    try:
        logger.info("Generating chord progression...")
        return chord_generator.generate_progression(
            style=request.style,
            start_degree=request.start_degree
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate_note_sequence/")
async def generate_note_sequence(chord_progression: str) -> List[str]:
    """Generate a note sequence based on a given chord progression."""
    try:
        logger.info("Generating note sequence...")
        progression = chord_generator.parse_progression(chord_progression)
        note_sequence = chord_generator.generate_notes_from_chord(progression)
        return note_sequence
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/progression/{progression_id}")
async def get_progression(progression_id: int) -> dict[str, str | int]:
    """Retrieve a specific chord progression by ID."""
    try:
        logger.info("Retrieving chord progression...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    # Logic to retrieve the progression based on ID (implement as needed)
    return {"progression_id": progression_id, "progression": "example"}

@app.get("/")
async def read_root() -> dict[str, str]:
    try:
        logger.info("Root endpoint accessed")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return {"message": "Welcome to the Chord Progression Generator API!"}

# Add more endpoints as needed

if __name__ == '__main__':
    # Run the Uvicorn server with the custom logging configuration
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config="logging_config.json")