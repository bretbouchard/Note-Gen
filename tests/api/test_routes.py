import pytest
from fastapi import FastAPI
from note_gen.app import app

def test_router_paths():
    """Test that all expected routes are registered."""
    routes = []
    for route in app.routes:
        try:
            routes.append(route.path)
        except AttributeError:
            # Some route types might not have a path attribute
            pass
    expected_paths = [
        '/api/v1/patterns',
        '/api/v1/sequences',
        '/api/v1/chord-progressions',
        '/api/v1/users',
        '/health',
        '/',
        '/docs',
        '/redoc',
        '/openapi.json'
    ]

    for path in expected_paths:
        assert any(route == path or route.startswith(path) for route in routes), f"Expected path {path} not found in routes"
