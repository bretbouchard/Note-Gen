"""Tests for user routes."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import APIRouter
from src.note_gen.routers.user_routes import router


def test_router_exists():
    """Test that the router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


def test_router_tags():
    """Test that the router has the correct tags."""
    assert "users" in router.tags
