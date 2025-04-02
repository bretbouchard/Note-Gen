from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "note_gen"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Note Generator API"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Validation
    DEFAULT_VALIDATION_LEVEL: str = "NORMAL"
    
    class Config:
        env_file = ".env"

settings = Settings()