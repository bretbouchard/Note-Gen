from pydantic import BaseModel, ConfigDict
from bson import ObjectId
from typing import List, Any, Optional
from src.note_gen.core.enums import ScaleType

class ChordProgressionResponse(BaseModel):
    id: Optional[str] = None
    name: str
    chords: List[str]
    key: str
    scale_type: ScaleType
    complexity: Optional[float] = 0.0
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            ObjectId: lambda v: str(v)
        }
    )

    @classmethod
    def from_db_model(cls, db_model: Any) -> 'ChordProgressionResponse':
        """Convert database model to response model."""
        return cls(
            id=str(db_model.id) if hasattr(db_model, 'id') and db_model.id is not None else None,
            name=db_model.name,
            chords=[str(chord) for chord in db_model.chords],
            key=db_model.key,
            scale_type=db_model.scale_type,
            complexity=db_model.complexity or 0.0,
            tags=db_model.tags if hasattr(db_model, 'tags') else [],
            created_at=db_model.created_at if hasattr(db_model, 'created_at') else None,
            updated_at=db_model.updated_at if hasattr(db_model, 'updated_at') else None
        )
