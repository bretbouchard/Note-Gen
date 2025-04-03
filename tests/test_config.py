"""Tests for the config module."""
import os
import pytest
from unittest.mock import patch
from note_gen.config import Settings


def test_settings_default_values():
    """Test that Settings has the expected default values."""
    settings = Settings()
    assert settings.mongodb_uri == "mongodb://localhost:27017/test_note_gen"
    assert settings.database_name == "test_note_gen"
    # Don't test TESTING as it may be set in the environment


def test_settings_from_env_vars():
    """Test that Settings can be configured from environment variables."""
    with patch.dict(os.environ, {
        "MONGODB_URI": "mongodb://testhost:27017",
        "DATABASE_NAME": "test_db",
        "TESTING": "1"
    }):
        settings = Settings()
        assert settings.mongodb_uri == "mongodb://testhost:27017"
        assert settings.database_name == "test_db"
        assert settings.TESTING == "1"


def test_settings_model_config():
    """Test the model config of Settings."""
    assert Settings.Config.env_file == ".env"
    assert Settings.Config.env_file_encoding == "utf-8"
    assert Settings.Config.extra == "allow"
