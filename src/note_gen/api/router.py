"""API router configuration."""
from fastapi import APIRouter

patterns_router = APIRouter()
sequences_router = APIRouter()
generate_router = APIRouter()
chord_progressions_router = APIRouter()
users_router = APIRouter()

# Your route definitions here...

# Make sure to export all routers
__all__ = [
    'patterns_router',
    'sequences_router',
    'generate_router',
    'chord_progressions_router',
    'users_router'
]
