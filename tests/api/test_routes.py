import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.note_gen.routers.router import router  # Import the actual router instance, not the module

def test_router_paths():
    app = FastAPI()
    app.include_router(router)  # Now using the router instance
    
    # Use route.path instead of accessing path directly
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    assert "/api/v1/patterns" in routes
    assert "/api/v1/chords" in routes
