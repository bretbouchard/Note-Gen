from fastapi import FastAPI
from src.note_gen.routers.user_routes import router as user_routes
from src.note_gen.database import get_db
from src.note_gen.import_presets import ensure_indexes, import_presets_if_empty
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

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