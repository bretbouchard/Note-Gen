from fastapi import FastAPI, Request
from src.note_gen.routers.user_routes import router as user_routes
from src.note_gen.routers.chord_progression_routes import router as chord_progression_routes
from src.note_gen.database import get_db
from src.note_gen.import_presets import ensure_indexes, import_presets_if_empty
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware

# Import the FastAPI app instance from the root main.py

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create MongoDB connection
    app.mongodb_client = AsyncIOMotorClient('mongodb://localhost:27017/')
    app.mongodb = app.mongodb_client.note_gen_db
    yield
    # Shutdown: Close MongoDB connection
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

# Include routers with prefixes to avoid conflicts
app.include_router(user_routes, prefix="/users")
app.include_router(chord_progression_routes, prefix="/api/chord-progressions")

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

@app.on_event("startup")
async def startup_event():
    try:
        async with get_db() as db:
            await ensure_indexes(db)
            await import_presets_if_empty(db)
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        raise SystemExit("Database initialization failed, shutting down.")

@app.on_event("shutdown")
async def shutdown_event():
    if logger:
        logger.info("Shutting down the application...")

async def main():
    async with get_db() as db:  
        await ensure_indexes(db)
        await import_presets_if_empty(db)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())