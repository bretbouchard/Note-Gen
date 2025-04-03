"""Tests for the API main module."""
import pytest
from fastapi import APIRouter
from note_gen.api.main import router


def test_router_instance():
    """Test that the router is an instance of APIRouter."""
    assert isinstance(router, APIRouter)
    assert router.routes == []  # Should be empty initially
