"""Tests for pattern routes."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import APIRouter
from src.note_gen.routers.pattern_routes import router


def test_router_exists():
    """Test that the router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


def test_router_prefix():
    """Test that the router has the correct prefix."""
    assert router.prefix == "/api/v1/patterns"


def test_router_tags():
    """Test that the router has the correct tags."""
    assert "patterns" in router.tags
