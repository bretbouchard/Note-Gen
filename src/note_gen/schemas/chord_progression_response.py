from pydantic import BaseModel
from bson import ObjectId
from typing import List

class ChordProgressionResponse(BaseModel):
    id: str
    name: str
    chords: List[str]
    key: str
    scale_type: str
    complexity: float

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: lambda v: str(v)
        }
