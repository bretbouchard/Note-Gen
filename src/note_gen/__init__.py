from fastapi import FastAPI
from .routers.chord_progression_routes import router as chord_progression_router
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

app.include_router(chord_progression_router)