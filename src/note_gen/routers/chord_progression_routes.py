"""Router for chord progression-related endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from bson import ObjectId

from src.note_gen.core.enums import ScaleType
from src.note_gen.schemas.chord_progression_request import ChordProgressionRequest, ProgressionGenerationRequest
from src.note_gen.schemas.chord_progression_response import ChordProgressionResponse
from src.note_gen.services.chord_progression_service import ChordProgressionService
from src.note_gen.dependencies.database import get_db

router = APIRouter(
    prefix="/chord-progressions",
    tags=["chord-progressions"]
)
