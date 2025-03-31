"""User model for authentication and authorization."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class User(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True
    )
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
