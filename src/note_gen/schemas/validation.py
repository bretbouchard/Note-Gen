from pydantic import BaseModel
from typing import List, Optional

class ValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str]
    details: Optional[dict] = None