from fastapi import FastAPI
from src.note_gen.routers.user_routes import router as user_routes
from src.note_gen.database import get_db
from src.note_gen.import_presets import ensure_indexes, import_presets_if_empty
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(user_routes)

@app.on_event("startup")
async def startup_event() -> None:
    try:
        async with get_db() as db:
            try:
                await ensure_indexes(db)
                await import_presets_if_empty(db)
            except Exception as e:
                logger.error(f"Error during database initialization: {e}")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Note Gen API!"}