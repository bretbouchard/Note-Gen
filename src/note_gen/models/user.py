"""
User model for the application.
"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class User(BaseModel):
    """User model."""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True
            }
        }
    )

    id: Optional[str] = Field(None, alias="_id")
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
