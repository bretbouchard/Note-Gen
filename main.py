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

load_dotenv()  # Load environment variables from .env file

# Get the absolute path to the logs directory
base_dir = os.path.dirname(os.path.abspath(__file__))


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

async def get_db():
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
        print('FastAPI application starting...')
    except Exception as e:
        print(f"Logging error: {e}")
    try:
        await run_imports()  # This will handle initialization and importing presets
    except Exception as e:
        try:
            print(f"Error during database initialization: {e}")
        except Exception as e:
            print(f"Logging error: {e}")
    try:
        print("Application started...")
    except Exception as e:
        print(f"Logging error: {e}")
    yield  # This is where the application runs
    try:
        print("Shutting down the application...")
    except Exception as e:
        print(f"Logging error: {e}")

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
        try:
            print("Generating chord progression...")
        except Exception as e:
            print(f"Logging error: {e}")
        return chord_generator.generate_progression(
            style=request.style,
            start_degree=request.start_degree
        )
    except ValueError as e:
        try:
            print(f"Error generating chord progression: {e}")
        except Exception as e:
            print(f"Logging error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate_note_sequence/")
async def generate_note_sequence(chord_progression: str) -> List[str]:
    """Generate a note sequence based on a given chord progression."""
    try:
        try:
            print("Generating note sequence...")
        except Exception as e:
            print(f"Logging error: {e}")
        progression = chord_generator.parse_progression(chord_progression)
        note_sequence = chord_generator.generate_notes_from_chord(progression)
        return note_sequence
    except Exception as e:
        try:
            print(f"Error generating note sequence: {e}")
        except Exception as e:
            print(f"Logging error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/progression/{progression_id}")
async def get_progression(progression_id: int) -> dict[str, str | int]:
    """Retrieve a specific chord progression by ID."""
    try:
        print("Retrieving chord progression...")
    except Exception as e:
        print(f"Logging error: {e}")
    # Logic to retrieve the progression based on ID (implement as needed)
    return {"progression_id": progression_id, "progression": "example"}

@app.get("/")
async def read_root() -> dict[str, str]:
    try:
        print("Root endpoint accessed")
    except Exception as e:
        print(f"Logging error: {e}")
    return {"message": "Welcome to the Chord Progression Generator API!"}

# Add more endpoints as needed

if __name__ == '__main__':
    # Run the Uvicorn server with the custom logging configuration
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config="logging_config.json")