"""Main FastAPI application."""
from fastapi import FastAPI
from .router import router

app = FastAPI(
    title="Note Generator API",
    description="API for musical pattern generation and manipulation",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")