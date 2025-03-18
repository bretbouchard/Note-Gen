import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    app.state.db = client[os.getenv('DB_NAME', 'note_gen')]
    yield
    # Shutdown
    client.close()

app = FastAPI(lifespan=lifespan)
