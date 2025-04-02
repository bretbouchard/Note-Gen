"""Tests for sequence routes."""
import pytest
from fastapi import APIRouter

from note_gen.routers.sequences import router


def test_router_exists():
    """Test that the router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


def test_router_tags():
    """Test that the router has the correct tags."""
    assert router.tags == ["sequences"]
