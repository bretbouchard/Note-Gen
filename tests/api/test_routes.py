import pytest
from fastapi import FastAPI
from src.note_gen.routers import router

def test_router_endpoints():
    app = FastAPI()
    app.include_router(router)
    routes = [route.path for route in app.routes]
    assert "/api/v1/note-sequences/generate" in routes
    assert "/api/v1/chord-progressions" in routes
