"""Tests for chord progression routes."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from note_gen.routers.chord_progression_routes import router
from note_gen.services.chord_progression_service import ChordProgressionService


def test_router_exists():
    """Test that the router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


def test_router_prefix():
    """Test that the router has the correct prefix."""
    assert router.prefix == "/chord-progressions"


def test_router_tags():
    """Test that the router has the correct tags."""
    assert router.tags == ["chord-progressions"]
