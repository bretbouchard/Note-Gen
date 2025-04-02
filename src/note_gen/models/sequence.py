from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Note(BaseModel):
    pitch: int
    duration: float
    velocity: int = 100

class NoteSequenceCreate(BaseModel):
    name: str
    notes: List[Note]
    tempo: int = 120
    description: Optional[str] = None

class NoteSequence(NoteSequenceCreate):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Test Sequence",
                "notes": [
                    {"pitch": 60, "duration": 1.0, "velocity": 100},
                    {"pitch": 62, "duration": 1.0, "velocity": 100}
                ],
                "tempo": 120
            }
        }
