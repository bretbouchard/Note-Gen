"""Tests for API main and router modules."""
import pytest
from fastapi import APIRouter
from src.note_gen.api.main import router
from src.note_gen.api.router import (
    patterns_router,
    sequences_router,
    generate_router,
    chord_progressions_router,
    users_router
)


def test_main_router_exists():
    """Test that the main router exists."""
    assert router is not None
    assert isinstance(router, APIRouter)


def test_patterns_router_exists():
    """Test that the patterns router exists."""
    assert patterns_router is not None
    assert isinstance(patterns_router, APIRouter)


def test_sequences_router_exists():
    """Test that the sequences router exists."""
    assert sequences_router is not None
    assert isinstance(sequences_router, APIRouter)


def test_generate_router_exists():
    """Test that the generate router exists."""
    assert generate_router is not None
    assert isinstance(generate_router, APIRouter)


def test_chord_progressions_router_exists():
    """Test that the chord progressions router exists."""
    assert chord_progressions_router is not None
    assert isinstance(chord_progressions_router, APIRouter)


def test_users_router_exists():
    """Test that the users router exists."""
    assert users_router is not None
    assert isinstance(users_router, APIRouter)
