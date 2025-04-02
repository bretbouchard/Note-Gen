"""
Database configuration settings.
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Original uppercase fields
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "test_note_gen" if os.getenv("TESTING") else "note_gen"

    # Additional fields from .env
    TESTING: str = "0"
    MONGODB_TEST_URI: str = "mongodb://localhost:27017/test_note_gen"
    MONGODB_URI: str = "mongodb://localhost:27017/test_note_gen"
    DATABASE_NAME: str = "test_note_gen"
    CLEAR_DB_AFTER_TESTS: str = "0"
    PYTHONPATH: str = "src"

    # Lowercase aliases for test compatibility
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_test_uri: str = "mongodb://localhost:27017/test_note_gen"
    mongodb_uri: str = "mongodb://localhost:27017/test_note_gen"
    database_name: str = "test_note_gen"
    test_mongodb_database: str = "test_note_gen"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from environment variables

settings = Settings()
