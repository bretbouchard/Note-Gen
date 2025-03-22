"""Main FastAPI application."""
from fastapi import FastAPI
from .routers.router import router
from .database.db import init_db, close_mongo_connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

app.include_router(router)
