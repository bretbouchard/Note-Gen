import pytest
from fastapi import FastAPI
from src.note_gen.main import app

def test_router_paths():
    """Test that all expected routes are registered."""
    routes = [route.path for route in app.routes]
    expected_paths = [
        '/api/v1/patterns',
        '/api/v1/note-sequences',
        '/health',
        '/',
        '/docs',
        '/redoc',
        '/openapi.json'
    ]
    
    for path in expected_paths:
        assert any(route == path or route.startswith(path) for route in routes), f"Expected path {path} not found in routes"
