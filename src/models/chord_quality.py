# src/models/chord_quality.py
from pydantic import BaseModel
from src.models.enums import ChordQualityType

class ChordQuality(BaseModel):
    quality: ChordQualityType