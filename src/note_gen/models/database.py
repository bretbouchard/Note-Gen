from pydantic import BaseModel, Field, field_validator
from typing import Optional

class DatabaseConfig(BaseModel):
    """Database configuration model"""
    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(..., min_length=1)
    collection: str = Field(..., min_length=1)
    username: Optional[str] = None
    password: Optional[str] = None
    
    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Host cannot be empty")
        return v.strip()
    
    @field_validator('database', 'collection')
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Database and collection names cannot be empty")
        return v.strip()