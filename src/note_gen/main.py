from fastapi import FastAPI, Request
from src.note_gen.routers.user_routes import router as user_routes
from src.note_gen.routers.chord_progression_routes import router as chord_progression_routes
from src.note_gen.routers.rhythm_pattern_routes import router as rhythm_pattern_routes
from src.note_gen.routers.note_pattern_routes import router as note_pattern_routes
from src.note_gen.database import get_db
from src.note_gen.import_presets import ensure_indexes, import_presets_if_empty
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from typing import AsyncGenerator

# Import the FastAPI app instance from the root main.py

import logging
import os

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', mode='a', encoding='utf-8'),  # Log to app.log
    ]
)
logger = logging.getLogger(__name__)
logger.debug("Logging configured successfully.")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: Create MongoDB connection
    app.mongodb_client = AsyncIOMotorClient('mongodb://localhost:27017/')
    app.mongodb = app.mongodb_client.note_gen_db
    try:
        async with get_db() as db:
            await ensure_indexes(db)
            await import_presets_if_empty(db)
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        raise SystemExit("Database initialization failed, shutting down.")
    yield
    # Shutdown: Close MongoDB connection
    app.mongodb_client.close()
    if logger:
        logger.info("Shutting down the application...")

app = FastAPI()
mongodb_client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://localhost:27017")
app.lifespan = lifespan

# Include routers with prefixes to avoid conflicts
app.include_router(user_routes, prefix="/users")
app.include_router(chord_progression_routes, prefix="/api")
app.include_router(rhythm_pattern_routes, prefix="/api")
app.include_router(note_pattern_routes, prefix="/api")

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error in route handler: {e}", exc_info=True)
            raise

app.add_middleware(LogMiddleware)

async def main():
    async with get_db() as db:  
        await ensure_indexes(db)
        await import_presets_if_empty(db)

if __name__ == '__main__':
    import asyncio
    logger.debug("Test log entry: Application has started successfully.")
    logger.debug("Test log entry: Application has started successfully.")
    asyncio.run(main())