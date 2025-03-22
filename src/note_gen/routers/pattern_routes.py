from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..dependencies import get_db
from ..models.patterns import RhythmPattern, NotePattern

router = APIRouter()

@router.get("/patterns")
async def get_patterns(db=Depends(get_db)) -> Dict[str, Any]:
    """Get all available patterns."""
    # For now, return some mock data
    return {
        "rhythm_patterns": [
            {
                "name": "Basic 4/4",
                "pattern": [1.0, 1.0, 1.0, 1.0],
                "time_signature": "4/4"
            }
        ],
        "note_patterns": [
            {
                "name": "C Major Triad",
                "pattern": [
                    {"note_name": "C", "octave": 4},
                    {"note_name": "E", "octave": 4},
                    {"note_name": "G", "octave": 4}
                ],
                "direction": "up"
            }
        ]
    }