from pydantic import BaseModel
from bson import ObjectId

class ChordProgressionResponse(BaseModel):
    id: str
    name: str
    chords: list
    key: str
    scale_type: str
    complexity: float

    class Config:
        from_attributes = True
        json_encoders = {
            ObjectId: lambda v: str(v)
        }
