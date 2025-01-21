from fastapi import FastAPI
from .routers.chord_progression_routes import router as chord_progression_router

app = FastAPI()

app.include_router(chord_progression_router)