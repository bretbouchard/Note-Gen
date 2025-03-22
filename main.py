import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from motor.motor_asyncio import AsyncIOMotorClient
from src.note_gen.utils.logging_utils import setup_logger, request_id_ctx_var
import uuid

# Set up logger
logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application")
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    app.state.db = client[os.getenv('DB_NAME', 'note_gen')]
    logger.info("Database connection established")
    yield
    # Shutdown
    logger.info("Shutting down application")
    client.close()
    logger.info("Database connection closed")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    # Generate request ID
    request_id = str(uuid.uuid4())
    request_id_ctx_var.set(request_id)
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response
